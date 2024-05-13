from django.db import models
from django.utils.translation import gettext_lazy as _


class GenderTypes(models.TextChoices):
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")


class UserTypes(models.TextChoices):
    ADMIN = "admin", _("Admin")
    TEACHER = "teacher", _("Teacher")
    STUDENT = "student", _("Student")
    EDUCATOR = "educator", _("Educator")
    KINDERGARTENER = "kindergartener", _("Kindergartener")
    WORKER = "worker", _("Worker")

    @classmethod
    def get_student_types(cls):
        return [cls.STUDENT.value, cls.KINDERGARTENER.value]

    @classmethod
    def get_worker_types(cls):
        return [cls.TEACHER.value, cls.EDUCATOR.value, cls.WORKER.value]


class UserShortTypes(models.TextChoices):
    STUDENT = "student", _("Student")
    WORKER = "worker", _("Worker")
