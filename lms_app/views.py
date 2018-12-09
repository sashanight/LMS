from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseServerError
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_email
from django.core import serializers
from uuid import uuid1
import json
from .models import *
from .additional_checks import *
from .decorators import is_authenticated


def index(request):
    return HttpResponse("Hello, World!")


@require_http_methods(["POST"])
def auth(request):
    if 'email' in request.POST and 'password' in request.POST:
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(e_mail=email)
            print(user.password)
            print(password)
            if user.check_password(password):
                access_token = AccessToken()
                access_token.user = user
                token = str(uuid1())
                while AccessToken.objects.filter(token=token).count() > 0:
                    token = str(uuid1())
                access_token.token = token
                access_token.save()

                return HttpResponse(json.dumps({'token': token}), status=200, content_type="application/json")
            else:
                return HttpResponse(status=406)
        except ObjectDoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponseServerError()
    else:
        return HttpResponse(status=400)


def check_password_complexity(password):
    min_length = 8
    if len(password) < min_length:
        return [False, "The new password must be at least %d characters long." % min_length]

    first_isalpha = password[0].isalpha()
    if all(c.isalpha() == first_isalpha for c in password):
        return [False, "The new password must contain at least one letter and at least one digit or" \
                                    " punctuation character."]

    return [True, "Good password"]


@require_http_methods(["POST"])
def registration(request):
    if 'verification_code' in request.POST and 'email' in request.POST and 'password' in request.POST:
        code = request.POST["verification_code"]
        e_mail = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(verification_code__iexact=code)

            try:
                validate_email(e_mail)
            except:
                return HttpResponse(json.dumps({'answer': "Bad e-mail"}), status=403, content_type="application/json")

            is_good_password = check_password_complexity(password)
            if is_good_password[0]:
                user.e_mail = e_mail
                user.set_password(password)
                user.save()
                return HttpResponse(json.dumps({'answer': "Success"}), status=201, content_type="application/json")
            else:
                return HttpResponse(json.dumps({'answer': is_good_password[1]}), status=403,
                                    content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponseServerError()
    else:
        return HttpResponse(status=400)


def get_profile(uid):
    try:
        user = User.objects.get(id=uid)
        serialized_obj = serializers.serialize('json', [user, ])
        obj_structure = json.loads(serialized_obj)
        data = json.dumps(obj_structure[0]['fields'])
        return HttpResponse(data, status=200, content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["GET"])
@is_authenticated
def get_my_profile(uid, request):
    return get_profile(uid)


@require_http_methods(["POST"])
@is_authenticated
def edit_my_profile(uid, request):
    try:
        user = User.objects.get(id=uid)

        const_fields = ['e_mail', 'fio']
        editable_fields = ['phone_number', 'hometown', 'person_info', 'password']

        for field in const_fields:
            if field in request.POST:
                return HttpResponse(json.dumps({'answer': "%s isn't editable" % field}), status=400,
                                    content_type="application/json")

        for key in request.POST.keys():
            if key not in editable_fields:
                continue
            if key == "links_to_profile":
                for profile_link in request.POST[key]:
                    if not link_to_profile_check(profile_link):
                        return HttpResponse(status=400)

                    profile_type = profile_link.split('.')[0]
                    user.linktoprofile_set.filter(link__startswith=profile_type).delete()

                    new_link = LinkToProfile()
                    new_link.link = profile_link
                    new_link.user = user
                    new_link.save()
            elif key == 'phone_number':
                new_number = request.POST['phone_number']
                if phone_number_check(new_number):
                    user['phone_number'] = new_number
                else:
                    return HttpResponse(status=400)
            elif key == 'password':
                if 'old_password' in request.POST:
                    if user.check_password(request.POST['old_password']):
                        user.password = request.POST['password']
                    else:
                        return HttpResponse(status=400)
                else:
                    return HttpResponse(status=400)
            else:
                user[key] = request.POST[key]

        user.save()
        return HttpResponse(status=200)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["GET"])
@is_authenticated
def get_user_profile(uid, request):
    if 'used_id' not in request.POST and 'link_to_user' not in request.POST:
        return HttpResponse(status=400)
    else:
        if 'used_id' in request.POST:
            return get_profile(request)
        else:
            try:
                link = request.POST['link_to_user']
                starts = ["https://vk.com/", "https://facebook.com/", "https://linkedin.com/", "https://instagram.com/"]
                if link.startswith(starts[0]):
                    user_id = User.objects.get(vk_link=link).user_id
                elif link.startswith(starts[1]):
                    user_id = User.objects.get(facebook_link=link).user_id
                elif link.startswith(starts[2]):
                    user_id = User.objects.get(linkedin_link=link).user_id
                elif link.startswith(starts[3]):
                    user_id = User.objects.get(instagram_link=link).user_id
                else:
                    return HttpResponse(status=400)
            except ObjectDoesNotExist:
                return HttpResponse(status=404)
            except Exception:
                return HttpResponseServerError()
            return get_profile(user_id)


@require_http_methods(["GET"])
@is_authenticated
def get_classmates(uid, request):
    try:
        student = Student.objects.get(id=uid)
        group_id = student.group_id
        classmates = Student.objects.filter(id=group_id)
        serialized_obj = serializers.serialize('json', classmates)
        obj_structure = json.loads(serialized_obj)
        data = json.dumps(obj_structure[0])
        return HttpResponse(data, status=200, content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["GET"])
@is_authenticated
def get_courses_list(uid, request):
    try:
        courses = None
        if Student.objects.filter(id=uid).exists():
            student = Student.objects.get(id=uid)
            group_name = student.group_name
            courses = Course.objects.filter(groups_of_course__group_name=group_name)
            # TODO по group_id

        elif Teacher.objects.filter(user_id=uid).exists():
            teacher = Teacher.objects.get(id=uid)
            courses = Course.objects.filter(course_instructors__FIO=teacher.fio)
            # TODO по user_id

        courses_list = []
        for course in courses:
            courses_list.append(course.course_name)
        data = json.dumps({"list_of_courses": courses_list})
        return HttpResponse(data, status=200, content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["GET"])
@is_authenticated
def get_course_info(uid, request):
    if 'course_name' in request.POST:
        try:
            course = Course.objects.get(course_name=request.POST["course_name"])
            serialized_obj = serializers.serialize('json', [course, ])
            obj_structure = json.loads(serialized_obj)

            materials = CourseMaterial.objects.filter(course=course)
            serialized_obj2 = serializers.serialize('json', materials)
            obj_structure2 = json.loads(serialized_obj2)

            tasks = Task.objects.filter(course=course)
            serialized_obj3 = serializers.serialize('json', tasks)
            obj_structure3 = json.loads(serialized_obj3)

            data = {'course_info': obj_structure[0], 'materials_info': obj_structure2[0],
                    'tasks_info': obj_structure3[0]}
            return HttpResponse(json.dumps(data), status=200, content_type="application/json")
        except ObjectDoesNotExist:
            return HttpResponse(status=404)
        except Exception:
            return HttpResponseServerError()
    else:
        return HttpResponse(status=400)


@require_http_methods(["POST"])
@is_authenticated
def manage_course_materials(uid, request):
    try:
        user = User.objects.get(id=uid)
        if "course_name" in request.POST and "course_material_body" in request.POST and "course_material_name" \
                in request.POST:
            course = Course.objects.get(course_name=request.POST['course_name'])
            if course.course_instructors.filter(fio=user.fio).exists() or course.trusted_individuals.filter(
                    fio=user.fio):

                if CourseMaterial.objects.filter(material_name=request.POST["course_material_name"]).exists():
                    material = CourseMaterial.objects.get(material_name=request.POST["course_material_name"])
                    if request.POST["course_material_body"]:
                        material.content = request.POST["course_material_body"]
                    else:
                        material.delete()
                else:
                    new_material = CourseMaterial()
                    new_material.course = course
                    new_material.material_name = request.POST["course_material_name"]
                    new_material.content = request.POST["course_material_body"]
                    new_material.start_date = datetime.datetime.now()
                    new_material.save()
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=400)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["POST"])
@is_authenticated
def add_trusted_individuals(uid, request):
    try:
        teacher = User.objects.get(id=uid)
        if "course_name" in request.POST and "trusted_individual_id" in request.POST:
            course = Course.objects.get(course_name=request.POST['course_name'])
            student = Student.objects.get(id=request.POST["trusted_individual_id"])
            if course.groups_of_course.filter(id=student.group.id).exists():
                pass
            else:
                return HttpResponse(status=403)

            if course.course_instructors.filter(fio=teacher.fio).exists():
                course.trusted_individuals.add(student)
            else:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=400)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["POST"])
@is_authenticated
def manage_course_task(uid, request):
    try:
        user = User.objects.get(user_id=uid)
        if "course_name" in request.POST and "task_body" in request.POST and "task_name" in request.POST:
            course = Course.objects.get(course_name=request.POST['course_name'])
            if course.course_instructors.filter(fio=user.fio).exists():
                if Task.objects.filter(task_name=request.POST["task_name"]).exists():
                    task = Task.objects.get(material_name=request.POST["task_name"])
                    if request.POST["task_body"]:
                        task.content = request.POST["task_body"]
                        if "task_start" in request.POST:
                            task.start = request.POST["task_start"]
                        if "task_end" in request.POST:
                            task.end = request.POST["task_end"]
                    else:
                        task.delete()
                else:
                    new_task = Task()
                    new_task.course = course
                    new_task.task_name = request.POST["task_name"]
                    new_task.description = request.POST["task_body"]
                    if "task_start" in request.POST:
                        new_task.start = request.POST["task_start"]
                    if "task_end" in request.POST:
                        new_task.end = request.POST["task_end"]
                    new_task.save()
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=400)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["POST"])
@is_authenticated
def upload_task_solution(uid, request):
    try:
        user = User.objects.get(id=uid)
        group_id = user.student.group.id
        if "course_name" in request.POST and "task_id" in request.POST and "solution_body" in request.POST:
            course = Course.objects.get(course_name=request.POST['course_name'])
            task = Task.objects.get(id=request.POST['task_id'])
            if course.groups_of_course.filter(id=group_id).exists():
                if TaskSolution.objects.filter(task=task, user=user).exists():
                    task_solution = TaskSolution.objects.get(task=task,user=user)
                    if request.POST["solution_body"]:
                        task_solution.solution = request.POST["solution_body"]
                    else:
                        task_solution.delete()
                else:
                    new_solution = TaskSolution()
                    new_solution.task = task
                    new_solution.user = user
                    new_solution.solution = request.POST["solution_body"]
                    new_solution.save()
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=400)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["GET"])
@is_authenticated
def watch_task_solution(uid, request):
    try:
        user = User.objects.get(id=uid)
        if "task_id" in request.GET:
            task = Task.objects.get(id=request.POST['task_id'])
            course = task.course
            groups = course.groups_of_course
            answer_dict = dict()
            if course.course_instructors.filter(id=user.id).exists():
                for group in groups:
                    solutions_dict = dict()
                    for user in User.objects.filter(Group=group):
                        try:
                            user_solution = TaskSolution.objects.get(user=user,task=task)
                            solutions_dict[user.fio] = {"Sent": "Yes", "Solution": user_solution.solution}
                        except:
                            solutions_dict[user.fio] = {"Sent": "No", "Solution": {}}
                    answer_dict[group.group_name] = solutions_dict
                return HttpResponse(json.dumps(answer_dict), status=200, content_type="application/json")
            else:
                return HttpResponse(status=403)
        else:
            return HttpResponse(status=400)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()