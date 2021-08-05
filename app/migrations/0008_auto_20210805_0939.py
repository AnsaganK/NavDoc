# Generated by Django 3.1.4 on 2021-08-05 09:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0007_auto_20210716_1111'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceNoteTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=250)),
                ('users', models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Тип СЗ',
                'verbose_name_plural': 'Типы СЗ',
            },
        ),
        migrations.AddField(
            model_name='servicenote',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.servicenotetypes'),
        ),
    ]