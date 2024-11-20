# Generated by Django 5.1 on 2024-11-20 09:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HandwritingAnalysisTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField(help_text='URL of the uploaded image', max_length=500)),
                ('recognized_text', models.TextField(help_text='Text recognized from the image')),
                ('analyzed_text', models.TextField(help_text='Analyzed or processed text')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp of when the record was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Timestamp of when the record was last updated', verbose_name='Updated At')),
                ('user', models.ForeignKey(help_text='User who uploaded the image', on_delete=django.db.models.deletion.CASCADE, related_name='handwriting_analyses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Handwriting Analysis',
                'verbose_name_plural': 'Handwriting Analyses',
                'ordering': ['-created_at'],
            },
        ),
    ]