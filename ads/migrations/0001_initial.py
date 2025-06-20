# Generated by Django 5.1.6 on 2025-05-25 11:32

import ads.models
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='unique identifier')),
                ('campaign_title', models.CharField(max_length=75, verbose_name='Campaign title')),
                ('tags', models.JSONField(default=list, help_text='Tags to match user interest')),
                ('start_datetime', models.DateField(null=True)),
                ('end_datetime', models.DateField(null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('active_ad_period', models.DurationField(blank=True, null=True)),
                ('limited_overdue', models.IntegerField(blank=True, null=True)),
                ('poster', models.ImageField(blank=True, help_text='Main image or media for the ad', null=True, upload_to=ads.models.ad_poster_upload_path)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AdSpace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Ad space name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug identifier (e.g. homepage-banner)')),
            ],
        ),
        migrations.CreateModel(
            name='AdType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserBehavior',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('session_id', models.CharField(blank=True, max_length=255, null=True)),
                ('page_slug', models.CharField(max_length=255)),
                ('category', models.CharField(blank=True, max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=255, unique=True)),
                ('interests', models.JSONField(default=list)),
                ('last_active', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AdImpression',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('session_id', models.CharField(blank=True, max_length=255, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user_agent', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ads.admanager')),
            ],
        ),
        migrations.CreateModel(
            name='AdClick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('referrer', models.TextField(blank=True)),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ads.admanager')),
            ],
        ),
        migrations.AddField(
            model_name='admanager',
            name='ad_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ads.adtype'),
        ),
        migrations.CreateModel(
            name='AdPlacement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(default=0, help_text='Order of ad in space')),
                ('is_primary', models.BooleanField(default=False, help_text='Mark if this is the primary ad for space')),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='placements', to='ads.admanager')),
                ('ad_space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='placements', to='ads.adspace')),
            ],
            options={
                'ordering': ['position'],
                'unique_together': {('ad', 'ad_space')},
            },
        ),
    ]
