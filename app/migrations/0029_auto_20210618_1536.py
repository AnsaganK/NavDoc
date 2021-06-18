# Generated by Django 3.1.4 on 2021-06-18 15:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0028_profile_isbuh'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicenote',
            name='buh',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_notes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='servicenote',
            name='isBuh',
            field=models.BooleanField(default=False),
        ),
    ]
