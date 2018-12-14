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


@require_http_methods(["GET", "POST"])
@is_authenticated
def my_profile_request(uid, request):
    if request.method == "GET":
        return get_my_profile(uid, request)
    elif request.method == "POST":
        return edit_my_profile(uid, request)


#@require_http_methods(["GET"])
#@is_authenticated
def get_my_profile(uid, request):
    return get_profile(uid)


#@require_http_methods(["POST"])
#@is_authenticated
def edit_my_profile(uid, request):
    try:
        user = User.objects.get(id=uid)

        const_fields = ['e_mail', 'fio']
        editable_fields = ['phone_number', 'hometown', 'person_info', 'password', 'vk_link', 'facebook_link',
                           'linkedin_link', 'instagram_link']
        link_fields = ['vk_link', 'facebook_link', 'linkedin_link', 'instagram_link']

        for field in const_fields:
            if field in request.POST:
                return HttpResponse(json.dumps({'answer': "%s isn't editable" % field}), status=400,
                                    content_type="application/json")

        for key in request.POST.keys():
            if key not in editable_fields:
                continue
            elif key == 'phone_number':
                new_number = request.POST['phone_number']
                if phone_number_check(new_number):
                    user.phone_number = new_number
                else:
                    return HttpResponse(status=400)
            elif key == 'password':
                if 'old_password' in request.POST:
                    if user.check_password(request.POST['old_password']):
                        user.set_password(request.POST['password'])
                    else:
                        return HttpResponse(status=400)
                else:
                    return HttpResponse(status=400)
            elif key in link_fields:
                if link_to_profile_check(request.POST[key]):
                    setattr(user, key, request.POST[key])
                else:
                    return HttpResponse(status=400)
            else:
                setattr(user, key, request.POST[key])

        user.save()
        return HttpResponse(status=200)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["GET"])
@is_authenticated
def get_user_profile_by_id(uid, request, user_id):
    print(uid, user_id)
    return get_profile(user_id)


@require_http_methods(["GET"])
@is_authenticated
def get_user_profile_by_link(uid, request, link_type, link_text):
    print(link_type, link_text)
    try:
        if link_type == "vk":
            user_id = User.objects.get(vk_link="https://vk.com/"+link_text).id
        elif link_type == "instagram":
            user_id = User.objects.get(instagram_link="https://instagram.com/"+link_text).id
        elif link_type == "facebook":
            user_id = User.objects.get(facebook_link="https://facebook.com/"+link_text).id
        elif link_type == "linkedin":
            user_id = User.objects.get(linkedin_link="https://linkedin.com/"+link_text).id
        else:
            return HttpResponse(status=400)
        return get_profile(user_id)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["GET"])
@is_authenticated
def get_classmates(uid, request):
    try:
        student = Student.objects.get(id=uid)
        group = student.group
        classmates = Student.objects.filter(group=group).exclude(id=uid)

        # TODO - хз как сериализовать все поля класса (не только дочернего)
        # #print(classmates)
        # serialized_obj = serializers.serialize('json', list(classmates))
        # obj_structure = json.loads(serialized_obj)
        # obj_structure = [obj['fields'] for obj in obj_structure]
        # #print(obj_structure)

        data = []
        field_to_answer = ['id', 'FIO', 'e_mail', 'vk_link', 'instagram_link', 'facebook_link',
                           'linkedin_link']
        for classmate in classmates:
            classmate_obj = dict()
            for field in field_to_answer:
                classmate_obj[field] = getattr(classmate,field)
            data.append(classmate_obj)
        return HttpResponse(json.dumps(data), status=200, content_type="application/json")
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
            group = student.group
            courses = Course.objects.filter(groups_of_course__in=[group])
            # TODO по group_id

        elif Teacher.objects.filter(id=uid).exists():
            teacher = Teacher.objects.get(id=uid)
            courses = Course.objects.filter(course_instructors__FIO=teacher.FIO)
            # TODO по user_id

        courses_list = []
        for course in courses:
            courses_list.append({"id": course.id, "course_name" : course.course_name})
        data = json.dumps({"list_of_courses": courses_list})
        return HttpResponse(data, status=200, content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["GET"])
@is_authenticated
def get_course_info(uid, request, course_name):
    try:
        print("HERE")
        course = Course.objects.get(course_name=course_name)
        serialized_obj = serializers.serialize('json', [course, ])
        obj_structure = json.loads(serialized_obj)

        materials = CourseMaterial.objects.filter(course=course)
        serialized_obj2 = serializers.serialize('json', materials)
        obj_structure2 = json.loads(serialized_obj2)

        tasks = Task.objects.filter(course=course)
        serialized_obj3 = serializers.serialize('json', tasks)
        obj_structure3 = json.loads(serialized_obj3)

        course_info = dict()
        course_info["course_id"] = course.id
        course_info["course_name"] = course.course_name
        course_info["description"] = course.description
        if course.trusted_individuals.count():
            print(course.trusted_individuals)
            print("FF")
            course_info["trusted_individuals"] = [{"id": student.id, "FIO": student.FIO}
                                                  for student in course.trusted_individuals.all()]
        else:
            course_info["trusted_individuals"] = []
        print("HERE##")
        course_info["course_materials"] = [{"id": material.id, "material_name": material.material_name,
                                            "content": material.content,
                                            "start_date": material.start_date.strftime("%Y-%m-%d %H:%M:%S")}
                                           for material in materials]
        course_info["course_tasks"] = [{"id": task.id, "task_name": task.task_name, "description": task.description,
                                        "start": task.start.strftime("%Y-%m-%d %H:%M:%S"),
                                        "end": task.end.strftime("%Y-%m-%d %H:%M:%S")} for task in tasks]
        print(course_info)

        return HttpResponse(json.dumps(course_info), status=200, content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()


@require_http_methods(["POST"])
@is_authenticated
def manage_course_materials(uid, request, course_name):
    try:
        user = User.objects.get(id=uid)
        if "course_material_name" in request.POST:
            course = Course.objects.get(course_name=course_name)
            if course.course_instructors.filter(id=user.id).exists() or course.trusted_individuals.filter(id=user.id):
                if CourseMaterial.objects.filter(material_name=request.POST["course_material_name"]).filter(
                        course=course).exists():
                    material = CourseMaterial.objects.get(course=course,
                                                          material_name=request.POST["course_material_name"])
                    if "course_material_body" in request.POST:
                        material.content = request.POST["course_material_body"]
                        material.save()
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
def add_trusted_individuals(uid, request, course_name):
    try:
        teacher = User.objects.get(id=uid)
        if "trusted_individual_id" in request.POST:
            course = Course.objects.get(course_name=course_name)
            student = Student.objects.get(id=request.POST["trusted_individual_id"])
            if course.groups_of_course.filter(id=student.group.id).exists():
                pass
            else:
                return HttpResponse(status=403)
            if course.course_instructors.filter(id=teacher.id).exists():
                course.trusted_individuals.add(student)
                course.save()
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
def manage_course_task(uid, request, course_name):
    try:
        user = User.objects.get(id=uid)
        if "task_name" in request.POST:
            course = Course.objects.get(course_name=course_name)
            if course.course_instructors.filter(id=user.id).exists():
                if Task.objects.filter(course=course).filter(task_name=request.POST["task_name"]).exists():
                    task = Task.objects.get(task_name=request.POST["task_name"], course=course)
                    if "task_body" in request.POST:
                        task.description = request.POST["task_body"]
                        if "task_start" in request.POST:
                            task.start = request.POST["task_start"]
                        if "task_end" in request.POST:
                            task.end = request.POST["task_end"]
                        task.save()
                    else:
                        task.delete()
                else:
                    new_task = Task()
                    new_task.course = course
                    new_task.task_name = request.POST["task_name"]
                    if "task_body" not in request.POST:
                        return HttpResponse(status=400)
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
def upload_task_solution(uid, request, course_name, task_id):
    try:
        user = User.objects.get(id=uid)
        group = user.student.group
        if "solution_body" in request.POST:
            course = Course.objects.get(course_name=course_name)
            task = Task.objects.get(id=task_id)
            if course.groups_of_course.filter(id=group.id).exists():
                if TaskSolution.objects.filter(task=task, user=user).exists():
                    task_solution = TaskSolution.objects.get(task=task,user=user)
                    if request.POST["solution_body"]:
                        task_solution.solution = request.POST["solution_body"]
                        task_solution.save()
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
def watch_task_solution(uid, request, course_name, task_id):
    try:
        user = User.objects.get(id=uid)
        task = Task.objects.get(id=task_id)
        course = task.course
        groups = course.groups_of_course.all()
        answer_dict = dict()
        if course.course_instructors.filter(id=user.id).exists():
            print("dd")
            for group in groups:
                solutions_dict = dict()
                for student in Student.objects.filter(group=group):
                    print(student.FIO)
                    try:
                        student_solution = TaskSolution.objects.get(user=student,task=task)
                        print(student_solution.id, "sid")
                        solutions_dict[student.FIO] = {"Sent": "Yes", "Solution": student_solution.solution}
                    except:
                        solutions_dict[student.FIO] = {"Sent": "No", "Solution": {}}
                answer_dict[group.group_name] = solutions_dict
            return HttpResponse(json.dumps(answer_dict), status=200, content_type="application/json")
        else:
            return HttpResponse(status=403)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)
    except Exception:
        return HttpResponseServerError()