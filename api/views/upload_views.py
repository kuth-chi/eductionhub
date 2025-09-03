import os
import uuid
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """
    Handle file uploads for school logos, cover images, etc.
    """
    # Add debugging before any authentication checks
    # logger.info("=== UPLOAD REQUEST DEBUG ===")
    # logger.info(f"Request method: {request.method}")
    # logger.info(f"Request path: {request.path}")
    # logger.info(f"User authenticated: {request.user.is_authenticated}")
    # logger.info(f"User: {request.user}"
    # logger.info(
    #     f"Authorization header: {request.META.get('HTTP_AUTHORIZATION', 'NOT PRESENT')}")
    # logger.info(
    #     f"All headers starting with HTTP_: {[k for k in request.META.keys() if k.startswith('HTTP_')]}")
    # for key in request.META.keys():
    #     if key.startswith('HTTP_'):
    #         logger.info(f"  {key}: {request.META[key]}")
    # logger.info("=== END UPLOAD DEBUG ===")

    try:
        # logger.info(f"Upload request received from user: {request.user}")
        # logger.info(f"Request FILES keys: {list(request.FILES.keys())}")
        # logger.info(f"Request POST keys: {list(request.POST.keys())}")
        # logger.info(f"Request headers: {dict(request.headers)}")
        # logger.info(
        #     f"Authorization header: {request.headers.get('Authorization', 'NOT PRESENT')}")
        # logger.info(
        #     f"User agent: {request.META.get('HTTP_USER_AGENT', 'Not found')}")
        # logger.info(
        #     f"Remote addr: {request.META.get('REMOTE_ADDR', 'Not found')}")
        # logger.info(f"User authenticated: {request.user.is_authenticated}")
        # logger.info(
        #     f"User ID: {request.user.id if request.user.is_authenticated else 'N/A'}"
        # )

        # Get the uploaded file
        uploaded_file = request.FILES.get("file")
        upload_type = request.POST.get("type", "general")

        if not uploaded_file:
            logger.error("No file provided in upload request")
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # logger.info(
        #     f"File received: {uploaded_file.name}, size: {uploaded_file.size}, type: {uploaded_file.content_type}"
        # )
        # logger.info(f"Upload type: {upload_type}")

        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if uploaded_file.content_type not in allowed_types:
            # logger.error(f"Invalid file type: {uploaded_file.content_type}")
            return Response(
                {
                    "error": f'File type {uploaded_file.content_type} not allowed. Allowed types: {", ".join(allowed_types)}'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate file size (5MB for logos, 10MB for covers)
        max_size = 5 * 1024 * 1024 if upload_type == "logo" else 10 * 1024 * 1024
        if uploaded_file.size > max_size:
            # logger.error(
            #     f"File too large: {uploaded_file.size} bytes, max: {max_size} bytes"
            # )
            return Response(
                {
                    "error": f"File size too large. Maximum size: {max_size // (1024 * 1024)}MB"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{upload_type}/{uuid.uuid4()}{file_extension}"

        # logger.info(f"Saving file to: {unique_filename}")

        # Save file to media storage
        try:
            file_path = default_storage.save(unique_filename, uploaded_file)
            # logger.info(f"File saved successfully to: {file_path}")

        except (OSError, ValueError) as e:
            logger.error("Failed to save file: %s", str(e))
            return Response(
                {"error": f"Failed to save file to server {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Generate URL
        try:
            file_url = default_storage.url(file_path)
            # logger.info(f"Generated file URL: {file_url}")

            # If using local storage, prepend the domain
            if not file_url.startswith("http"):
                file_url = f"{request.build_absolute_uri('/')[:-1]}{file_url}"
                # logger.info(f"Updated file URL with domain: {file_url}")
        except (OSError, ValueError) as e:
            logger.error("Failed to generate URL: %s", str(e))

            return Response(
                {"error": f"Failed to generate file URL {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_data = {
            "url": file_url,
            "filename": os.path.basename(file_path),
            "size": uploaded_file.size,
            "type": upload_type,
        }

        # logger.info(f"Upload successful, returning: {response_data}")

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )

    except (OSError, ValueError) as e:
        # logger.error(f"Upload failed with exception: {str(e)}", exc_info=True)
        return Response(
            {"error": f"Upload failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
