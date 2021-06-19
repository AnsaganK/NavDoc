# Generated by Django 3.1.7 on 2021-06-19 20:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.FileField(blank=True, null=True, upload_to='department_pictures')),
                ('name', models.CharField(max_length=200)),
                ('archive', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Отдел',
                'verbose_name_plural': 'Отделы',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('code', models.CharField(blank=True, max_length=120, null=True)),
            ],
            options={
                'verbose_name': 'Роль',
                'verbose_name_plural': 'Роли',
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
            },
        ),
        migrations.CreateModel(
            name='ServiceNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(blank=True, null=True)),
                ('title', models.CharField(max_length=120)),
                ('text', models.TextField()),
                ('summa', models.CharField(blank=True, max_length=200, null=True)),
                ('fast', models.BooleanField(default=False)),
                ('date_create', models.DateTimeField(auto_now_add=True)),
                ('date_update', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('user_index', models.IntegerField(blank=True, default=1, null=True)),
                ('status', models.CharField(blank=True, choices=[('success', 'Подписать'), ('edit', 'На редактирование'), ('error', 'Отказать')], max_length=200, null=True)),
                ('isChef', models.BooleanField(blank=True, default=False, null=True)),
                ('isBuh', models.BooleanField(blank=True, default=False, null=True)),
                ('buh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(related_name='notes', to='app.Tags')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Служебная записка',
                'verbose_name_plural': 'Служебные записки',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.FileField(blank=True, null=True, upload_to='users_avatar')),
                ('position', models.CharField(blank=True, max_length=300, null=True)),
                ('patronymic', models.CharField(blank=True, max_length=120, null=True)),
                ('signature', models.FileField(blank=True, null=True, upload_to='user_signatures')),
                ('is_admin', models.BooleanField(default=False)),
                ('mobile', models.CharField(blank=True, max_length=100, null=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('blocked', models.BooleanField(default=False)),
                ('token', models.TextField(blank=True, null=True)),
                ('isChef', models.BooleanField(blank=True, default=False, null=True)),
                ('isBuh', models.BooleanField(blank=True, default=False, null=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='profiles', to='app.department')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='users', to='app.role')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='NoteUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('success', 'Подписать'), ('edit', 'На редактирование'), ('error', 'Отказать')], max_length=200, null=True)),
                ('date_create', models.DateTimeField(auto_now=True, null=True)),
                ('is_read', models.BooleanField(default=False)),
                ('date_read', models.DateTimeField(blank=True, null=True)),
                ('note', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='app.servicenote')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='note', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Подписывающий',
                'verbose_name_plural': 'Подписывающие',
                'ordering': ['index'],
            },
        ),
        migrations.CreateModel(
            name='NoteFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='note_files/')),
                ('note', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='app.servicenote')),
            ],
            options={
                'verbose_name': 'Файл для записки',
                'verbose_name_plural': 'Файлы для записок',
            },
        ),
    ]
