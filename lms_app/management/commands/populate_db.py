from django.core.management.base import BaseCommand
from lms_app.models import *


class Command(BaseCommand):
    def _drop_db(self):
        TaskSolution.objects.all().delete()
        Task.objects.all().delete()
        CourseMaterial.objects.all().delete()
        Course.objects.all().delete()
        AccessToken.objects.all().delete()
        Teacher.objects.all().delete()
        Student.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()

    def _create_db(self):
        # GROUPS

        group_492 = Group(group_name="492", department_name="diht", course_number=4)
        group_492.save()

        group_493 = Group(group_name="493", department_name="diht", course_number=4)
        group_493.save()

        group_431 = Group(group_name="431", department_name="dasr", course_number=4)
        group_431.save()

        # TEACHERS

        teacher = Teacher(FIO="Ivanov", e_mail='ivanov@example.com')
        teacher.set_password('password1')
        teacher.save()

        teacher2 = Teacher(FIO="Kuznetsov", e_mail='kuznetsov@example.com')
        teacher2.set_password('password2')
        teacher2.save()

        teacher3 = Teacher(FIO="Frolov", e_mail='frolov@example.com')
        teacher3.set_password('password3')
        teacher3.save()

        teacher4 = Teacher(FIO="Popov", e_mail='popov@example.com')
        teacher4.set_password('password4')
        teacher4.save()

        # STUDENTS

        student = Student(FIO="Vasilyev", e_mail='vasilyev@example.com', degree='Bachelor',
                          form_of_study='Full-time', learning_base='Budget', group=group_492)
        student.set_password('password5')
        student.save()

        student2 = Student(FIO="Petrov", e_mail='petrov@example.com', degree='Bachelor',
                           form_of_study='Full-time', learning_base='Budget', group=group_492)
        student2.set_password('password6')
        student2.save()

        student3 = Student(FIO="Sokolov", e_mail='sokolov@example.com', degree='Bachelor',
                           form_of_study='Full-time', learning_base='Budget', group=group_493)
        student3.set_password('password7')
        student3.save()

        student4 = Student(FIO="Mikhailov", e_mail='mikhailov@example.com', degree='Bachelor',
                           form_of_study='Full-time', learning_base='Budget', group=group_493)
        student4.set_password('password8')
        student4.save()

        student5 = Student(FIO="Novikov", e_mail='novikov@example.com', degree='Bachelor',
                           form_of_study='Full-time', learning_base='Budget', group=group_431)
        student5.set_password('password9')
        student5.save()

        student6 = Student(FIO="Fedorov", e_mail='fedorov@example.com', degree='Bachelor',
                           form_of_study='Full-time', learning_base='Budget', group=group_431)
        student6.set_password('password10')
        student6.save()

        # COURSES

        course1 = Course(course_name="Matan")
        course1.save()
        course1.groups_of_course.add(group_492)
        course1.groups_of_course.add(group_493)
        course1.groups_of_course.add(group_431)
        course1.course_instructors.add(teacher)
        course1.trusted_individuals.add(student)
        course1.trusted_individuals.add(student3)
        course1.trusted_individuals.add(student5)
        course1.save()

        course2 = Course(course_name="Linal")
        course2.save()
        course2.groups_of_course.add(group_492)
        course2.groups_of_course.add(group_493)
        course2.groups_of_course.add(group_431)
        course2.course_instructors.add(teacher2)
        course2.trusted_individuals.add(student2)
        course2.trusted_individuals.add(student4)
        course2.trusted_individuals.add(student6)
        course2.save()

        course3 = Course(course_name="Phylosophy")
        course3.save()
        course3.groups_of_course.add(group_492)
        course3.groups_of_course.add(group_493)
        course3.course_instructors.add(teacher3)
        course3.trusted_individuals.add(student)
        course3.trusted_individuals.add(student3)
        course3.save()

        course4 = Course(course_name="Physics")
        course4.save()
        course4.groups_of_course.add(group_431)
        course4.course_instructors.add(teacher4)
        course4.trusted_individuals.add(student5)
        course4.save()

        # COURSE MATERIALS

        course_material = CourseMaterial(material_name="Functions", course=course1, content='Function is ..')
        course_material.save()

        course_material2 = CourseMaterial(material_name="Vectors", course=course2, content='Vector is ..')
        course_material2.save()

        course_material3 = CourseMaterial(material_name="Spinoza", course=course3, content='Baruh Ezpinosha')
        course_material3.save()

        course_material4 = CourseMaterial(material_name="Termodynamics", course=course4, content='Furie law')
        course_material4.save()

        # TASKS

        task = Task(task_name="Solve equations", course=course1, description='Number 3.42',
                    start=datetime.datetime.now(),
                    end=datetime.datetime.now() + datetime.timedelta(days=7))
        task.save()

        task2 = Task(task_name="Solve hard equation", course=course1, description='Number 3.49',
                     start=datetime.datetime.now(),
                     end=datetime.datetime.now() + datetime.timedelta(days=7))
        task2.save()

        task3 = Task(task_name="HW 1", course=course2, description='Number 1.1', start=datetime.datetime.now(),
                     end=datetime.datetime.now() + datetime.timedelta(days=7))
        task3.save()

        task4 = Task(task_name="1", course=course4, description='Tasks 1.1 - 1.8', start=datetime.datetime.now(),
                     end=datetime.datetime.now() + datetime.timedelta(days=7))
        task4.save()

        # TASKS SOLUTIONS

        # for task1
        task_solution = TaskSolution(task=task, user=student, solution="Answer= 1.23")
        task_solution.save()

        task_solution2 = TaskSolution(task=task, user=student2, solution="Answer=4.5")
        task_solution2.save()

        task_solution3 = TaskSolution(task=task, user=student3, solution="Answer=4.5")
        task_solution3.save()

        task_solution4 = TaskSolution(task=task, user=student5, solution="Answer=2.2")
        task_solution4.save()

        # for task2
        task_solution5 = TaskSolution(task=task2, user=student, solution="Answer=1.0")
        task_solution5.save()

        task_solution6 = TaskSolution(task=task2, user=student3, solution="Answer=1.0")
        task_solution6.save()

        # for task3
        task_solution7 = TaskSolution(task=task3, user=student, solution="Vector=(1,0,0)")
        task_solution7.save()

        task_solution8 = TaskSolution(task=task3, user=student6, solution="Vector=(3,4,2)")
        task_solution8.save()

        # for task4

        task_solution9 = TaskSolution(task=task4, user=student5, solution="Temperature = 10.0")
        task_solution9.save()

        task_solution10 = TaskSolution(task=task4, user=student6, solution="Temperature = 200.0")
        task_solution10.save()

    def handle(self, *args, **options):
        self._drop_db()
        self._create_db()

# def main():
#     drop_db()
#
# if __name__ == "__main__":
#     main()
