# Generated manually to revert to ImageField

from django.db import migrations, models
import schools.models.school


class Migration(migrations.Migration):

    dependencies = [
        ("schools", "0015_flexible_image_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="school",
            name="logo",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=schools.models.school.school_logo_upload_path,
                verbose_name="logo",
            ),
        ),
        migrations.AlterField(
            model_name="school",
            name="cover_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=schools.models.school.school_cover_image_upload_path,
                verbose_name="photo",
            ),
        ),
    ]
