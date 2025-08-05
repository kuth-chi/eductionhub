# Generated manually to fix image URL issues

from django.db import migrations, models
import schools.models.school


class Migration(migrations.Migration):

    dependencies = [
        ("schools", "0014_merge_20250727_0752"),
    ]

    operations = [
        migrations.AlterField(
            model_name="school",
            name="logo",
            field=models.CharField(
                blank=True, max_length=500, null=True, verbose_name="logo"
            ),
        ),
        migrations.AlterField(
            model_name="school",
            name="cover_image",
            field=models.CharField(
                blank=True, max_length=500, null=True, verbose_name="photo"
            ),
        ),
    ]
