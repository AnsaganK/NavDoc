from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse


class Role(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


class Tags(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"


class ServiceNote(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="notes")
    number = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=120)
    text = models.TextField()
    summa = models.CharField(max_length=200, null=True, blank=True)
    fast = models.BooleanField(default=False)
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(Tags, null=True, blank=True, related_name="notes")
    user_index = models.IntegerField(default=1, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("note_detail", args=[str(self.pk)])

    class Meta:
        verbose_name = "Служебная записка"
        verbose_name_plural = "Служебные записки"


statuses = (
    ("success", "Подписать"),
    ("edit", "На редактирование"),
    ("error", "Отказать"),
)


class NoteUsers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="note")
    note = models.ForeignKey(ServiceNote, on_delete=models.CASCADE, related_name="users")
    index = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=200,choices=statuses, null=True, blank=True)

    def __str__(self):
        return self.note.title

    class Meta:
        verbose_name = "Подписывающий"
        verbose_name_plural = "Подписывающие"


class Department(models.Model):
    picture = models.FileField(upload_to='department_pictures', null=True, blank=True)
    name = models.CharField(max_length=200)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('department_detail', args=[str(self.pk)])

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"


class NoteFiles(models.Model):
    note = models.ForeignKey(ServiceNote, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="note_files/")

    def __str__(self):
        return self.note.title

    class Meta:
        verbose_name = "Файл для записки"
        verbose_name_plural = "Файлы для записок"


class Profile(models.Model):
    picture = models.FileField(upload_to="users_avatar", null=True, blank=True)
    position = models.CharField(max_length=300, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    signature = models.FileField(upload_to='user_signatures', null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, blank=True, related_name="users")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True, related_name="profiles")
    mobile = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
