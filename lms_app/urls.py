from django.conf.urls import url

from . import views

app_name = 'lms_app'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^auth$', views.auth, name='auth'),
    url(r'^auth$', views.registration, name='registration'),
    url(r'^auth$', views.get_my_profile, name='get_my_profile'),
    url(r'^auth$', views.edit_my_profile, name='edit_my_profile')
]