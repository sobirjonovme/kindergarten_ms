from django.db import models
from django.utils.translation import gettext_lazy as _


class UserTypes(models.TextChoices):
    ADMIN = "admin", _("Admin")
    TEACHER = "teacher", _("Teacher")
    STUDENT = "student", _("Student")
    EDUCATOR = "educator", _("Educator")
    KINDERGARTENER = "kindergartener", _("Kindergartener")
    WORKER = "worker", _("Worker")
