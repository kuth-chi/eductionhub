import logging
import os
import faiss
import numpy as np
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from sentence_transformers import SentenceTransformer
from schools.models.schoolsModel import School
from openai import OpenAI  # Official OpenAI SDK v1.0+

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load tokens and keys
TELEGRAM_TOKEN = settings.TELEGRAM_LOGIN_PUBLIC_KEY
OPENAI_API_KEY = settings.OPEN_AI_API_SECRET

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key missing! Set OPENAI_API_KEY env var or in settings.")

# Initialize OpenAI client (best practice)
client = OpenAI(api_key=OPENAI_API_KEY)

# Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Globals for FAISS index and data
school_index = None
school_objs = []
THRESHOLD = 2.0  # Distance threshold for similarity


def build_school_index():
    global school_index, school_objs
    schools = School.objects.filter(is_active=True).prefetch_related("type")
    if not schools.exists():
        logger.warning("No active schools found to index.")
        return None

    texts = []
    for s in schools:
        try:
            type_names = ", ".join(getattr(t, "name", "Unknown") for t in s.type.all())
        except Exception:
            type_names = "Unknown"

        texts.append(
            f"{s.name}. Also known as {s.short_name} or {s.local_name}. "
            f"Located in {s.location}. Description: {s.description}. "
            f"Founded by {s.founder}. President: {s.president}. Motto: {s.motto}. Type: {type_names}."
        )

    embeddings = embedding_model.encode(texts, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

    school_objs = list(schools)
    return index


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Ask me anything about schools in our database. "
        "You can say things like 'Tell me about international schools' or 'What schools are in Phnom Penh?'"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text.strip()
    logger.info(f"Received question: {user_question}")

    results = get_answer_from_data(user_question)

    if isinstance(results, str):
        # Error or no data message
        await update.message.reply_text(results)
        return

    # results is a list of tuples: (raw_text, lat, lon, detail_url)
    for raw_text, lat, lon, detail_url in results:
        # Rephrase with OpenAI GPT
        friendly_text = await rephrase_text_with_openai(raw_text)

        buttons = []
        if lat is not None and lon is not None:
            try:
                lat_val = float(lat)
                lon_val = float(lon)
                buttons.append(
                    [
                        InlineKeyboardButton(
                            "📍 Open in Maps",
                            url=f"https://www.google.com/maps/search/?api=1&query={lat_val},{lon_val}",
                        )
                    ]
                )
            except ValueError:
                pass

        if detail_url:
            buttons.append([InlineKeyboardButton("📘 View Details", url=detail_url)])

        await update.message.reply_text(
            friendly_text,
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


def get_answer_from_data(question: str):
    if not school_index:
        return "⚠️ Sorry, school data is not ready yet. Please try again later."

    question_embedding = embedding_model.encode([question])
    D, I = school_index.search(np.array(question_embedding), k=5)

    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx >= len(school_objs) or dist > THRESHOLD:
            continue

        school = school_objs[idx]

        lat, lon = None, None
        if school.location and "," in school.location:
            try:
                parts = school.location.split(",")
                lat = parts[0].strip()
                lon = parts[1].strip()
            except Exception:
                lat, lon = None, None


        app_url = settings.APP_URL[0]
        if settings.DEBUG: 
            app_url = "http://localhost:8000"
        detail_url = f"{app_url}/en/schools/{school.pk}/"

        raw_text = (
            f"School Name: {school.name}\n"
            f"Local Name: {school.local_name}\n"
            f"Established: {school.established or 'N/A'}\n"
            f"President: {school.president or 'N/A'}\n"
            f"Description: {school.description[:400]}...\n"
        )
        results.append((raw_text, lat, lon, detail_url))

    if not results:
        return "🤖 Sorry, I couldn't find any relevant schools. Try rephrasing your question!"

    return results


async def rephrase_text_with_openai(text: str) -> str:
    """
    Use OpenAI GPT to rephrase the school info into a friendly, engaging message.
    Falls back to original text if API call fails.
    """
    prompt = (
        "You are a friendly assistant that helps users learn about schools. "
        "Rewrite the following factual data about a school into a warm, helpful, and engaging message:\n\n"
        f"{text}\n\n"
        "Reply in a clear, positive tone, under 500 characters."
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return text  # fallback to raw text


class Command(BaseCommand):
    help = "Run Telegram bot with AI-powered Q&A from School model"

    def handle(self, *args, **options):
        global school_index
        self.stdout.write(self.style.SUCCESS("🔁 Building school index..."))
        school_index = build_school_index()
        if not school_index:
            self.stderr.write(self.style.ERROR("🚫 Failed to build school index. Exiting."))
            return

        self.stdout.write(self.style.SUCCESS("✅ School index built."))

        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        self.stdout.write(self.style.SUCCESS("🤖 Bot is running and listening for messages..."))
        app.run_polling()
