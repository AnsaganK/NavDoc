from django.conf.urls import url

from app.views import NoteList, MyNoteList, MyNoteDetail, UserLogin, UserDetail

urlpatterns = [
    url(r'^login$', UserLogin.as_view()),
    url(r'^send_notes/(?P<pk>[0-9]+)$', NoteList.as_view()),
    url(r'^my_notes/(?P<pk>[0-9]+)$', MyNoteList.as_view()),
    url(r'^note/(?P<pk>[0-9]+)$', MyNoteDetail.as_view()),
    url(r'^profile/(?P<pk>[0-9]+)$', UserDetail.as_view()),
    #url(r'^user/(?P<pk>[0-9]+)/last-movies$', LastMovies.as_view()),
]
