from django.contrib.auth.models import User
from django.db.models import F

from .models import ServiceNote, NoteUsers


def unReadNotes(request):
    if request.user.is_anonymous:
        return {}
    user = request.user
    if request.user.profile.isChef:
        unReadCount = NoteUsers.objects.filter(user=user).filter(note__user_index__gte=F('index')).order_by(
            '-pk').filter(is_read=False).filter(note__isBuh=True).count()
    else:
        unReadCount = NoteUsers.objects.filter(user=user).filter(note__user_index__gte=F('index')).order_by(
            '-pk').filter(is_read=False).count()
    return {
        "unReadCount": unReadCount
    }