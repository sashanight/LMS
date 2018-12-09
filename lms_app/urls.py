from django.conf.urls import url

from . import views

app_name = 'lms_app'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^auth$', views.auth, name='auth'),
    url(r'^registration$', views.registration, name='registration'),
    url(r'^get_my_profile$', views.get_my_profile, name='get_my_profile'),
    url(r'^edit_my_profile$', views.edit_my_profile, name='edit_my_profile'),
    url(r'^get_user_profile$', views.get_user_profile, name='get_user_profile'),
    url(r'^get_classmates', views.get_classmates, name='get_classmates'),
    url(r'^get_courses_list', views.get_courses_list, name='get_courses_list'),
    url(r'^get_course_info', views.get_course_info, name='get_course_info'),
    url(r'^manage_course_materials', views.manage_course_materials, name='manage_course_materials'),
    url(r'^add_trusted_individuals', views.add_trusted_individuals, name='add_trusted_individuals'),
    url(r'^manage_course_task', views.manage_course_task, name='manage_course_task'),
    url(r'^upload_task_solution', views.upload_task_solution, name='upload_task_solution'),
    url(r'^watch_task_solution', views.watch_task_solution, name='watch_task_solution')
]