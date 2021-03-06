"""navistar_documents URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static


from django.contrib.auth import views as acc

from app.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/', include('app.url_api')),
    path('', include('app.urls')),
]

urlpatterns += [
    path('accounts/login/', acc.LoginView.as_view(), name='login'),
    path('accounts/logout/', acc.LogoutView.as_view(), name='logout'),
    path('accounts/password-reset', acc.PasswordResetView.as_view(), name='password_reset'),
    #path('', home, name='password_change_done'),
    #path('password-change', acc.PasswordChangeView.as_view(), name='password_change'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
