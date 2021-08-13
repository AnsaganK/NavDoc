# Generated by Django 3.1.4 on 2021-08-13 09:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0014_auto_20210812_1017'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuhStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('success', 'Одобрено'), ('edit', 'На редактирование'), ('error', 'Отказано')], default='success', max_length=256)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to=settings.AUTH_USER_MODEL, verbose_name='Бухгалтер')),
            ],
            options={
                'verbose_name': 'Статус бухгалтера',
                'verbose_name_plural': 'Статусы бухгалтеров',
            },
        ),
        migrations.AddField(
            model_name='servicenote',
            name='buh_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='notes', to='app.buhstatus'),
        ),
    ]
