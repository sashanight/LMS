from django.conf.urls import url

from . import views

app_name = 'lms_app'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^authentication$', views.auth, name='authentication'),
    url(r'^registration$', views.registration, name='registration'),
    url(r'^my_profile$', views.my_profile_request, name='my_profile'),
    # url(r'^get_my_profile$', views.get_my_profile, name='get_my_profile'),
    # url(r'^edit_my_profile$', views.edit_my_profile, name='edit_my_profile'),
    url(r'^user_profile/(?P<user_id>[a-z0-9\-]+)$', views.get_user_profile_by_id, name='user_profile'),
    url(r'^user_profile/(?P<link_type>[a-z0-9\-]+):(?P<link_text>[a-zA-Z0-9\-]+)$', views.get_user_profile_by_link,
        name='user_profile'),
    url(r'^my_classmates$', views.get_classmates, name='my_classmates'),
    url(r'^courses_list$', views.get_courses_list, name='courses_list'),
    url(r'^courses/(?P<course_name>[a-zA-Z0-9\-]+)$', views.get_course_info, name='course_info'),
    url(r'^courses/(?P<course_name>[a-zA-Z0-9\-]+)/materials$', views.manage_course_materials,
        name='course_materials'),
    url(r'^courses/(?P<course_name>[a-zA-Z0-9\-]+)/trusted_individuals$', views.add_trusted_individuals,
        name='trusted_individuals'),
    url(r'^courses/(?P<course_name>[a-zA-Z0-9\-]+)/tasks$', views.manage_course_task, name='course_task'),
    url(r'^courses/(?P<course_name>[a-zA-Z0-9\-]+)/tasks/(?P<task_id>[a-zA-Z0-9\-]+)/task_solutions$',
        views.upload_task_solution, name='task_solutions'),
    url(r'^courses/(?P<course_name>[a-zA-Z0-9\-]+)/tasks/(?P<task_id>[a-zA-Z0-9\-]+)/passed_solutions',
        views.watch_task_solution, name='passed_solutions')
]