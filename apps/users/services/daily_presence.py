from datetime import timedelta

from django.utils import timezone

from apps.common.services.date_time import find_diff_two_time
from apps.users.choices import FaceIDLogTypes, UserTypes
from apps.users.models import FaceIDLog, UserPresence


class UserDailyPresence:
    def __init__(self, user, date):
        self.user = user
        self.date = date

        self.day_start = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
        self.day_end = self.day_start + timedelta(days=1)

        self.enter_time = None
        self.exit_time = None

    def find_enter_exit_time(self):
        """
        Find enter and exit time for the user
        """
        face_id_logs = FaceIDLog.objects.filter(
            user=self.user, time__gte=self.day_start, time__lt=self.day_end
        ).order_by("time")

        enter_log = face_id_logs.filter(type=FaceIDLogTypes.ENTER).first()
        if enter_log:
            self.enter_time = timezone.localtime(enter_log.time).time()
        exit_log = face_id_logs.filter(type=FaceIDLogTypes.EXIT).last()
        if exit_log:
            self.exit_time = timezone.localtime(exit_log.time).time()

    def calculate_total_working_hours(self):
        """
        Calculate the amount of hours the user should actually work
        """
        work_start_time = self.user.work_start_time
        work_end_time = self.user.work_end_time
        if not work_start_time or not work_end_time:
            return 0

        diff = find_diff_two_time(end_time=work_end_time, begin_time=work_start_time)
        return round(diff.total_seconds() / 3600, 1)

    def calculate_worked_hour(self):
        """
        Calculate working hours for the user
        """
        if not self.enter_time or not self.exit_time:
            return 0

        work_start_time = self.user.work_start_time
        work_end_time = self.user.work_end_time
        if not work_start_time or not work_end_time:
            return 0

        if self.user.type not in UserTypes.get_worker_types():
            diff = self.exit_time - self.enter_time
            return round(diff.total_seconds() / 3600, 1)

        # if the user is a worker
        enter_diff = find_diff_two_time(end_time=self.enter_time, begin_time=work_start_time)
        if enter_diff < timedelta(minutes=20):
            time_begin = work_start_time
        elif enter_diff < timedelta(hours=1):
            time_begin = work_start_time
            time_begin = time_begin.replace(hour=time_begin.hour + 1)
        else:
            time_begin = self.enter_time

        exit_diff = find_diff_two_time(end_time=work_end_time, begin_time=self.exit_time)
        if exit_diff < timedelta(minutes=5):
            time_end = work_end_time
        elif exit_diff < timedelta(hours=1):
            time_end = work_end_time
            time_end = time_end.replace(hour=time_end.hour - 1)
        else:
            time_end = self.exit_time

        diff = find_diff_two_time(end_time=time_end, begin_time=time_begin)
        working_hours = round(diff.total_seconds() / 3600, 1)
        return working_hours

    def store_daily_presence(self):
        """
        Store daily presence time for the user
        """
        self.find_enter_exit_time()

        if not self.enter_time and not self.exit_time:
            return False

        is_created = False
        user_presence = UserPresence.objects.filter(user=self.user, date=self.date).first()

        if not user_presence:
            user_presence = UserPresence(user=self.user, date=self.date)
            is_created = True

        if self.enter_time:
            user_presence.enter_at = self.enter_time
        if self.exit_time:
            user_presence.exit_at = self.exit_time

        user_presence.work_start_time = self.user.work_start_time
        user_presence.work_end_time = self.user.work_end_time
        user_presence.present_time = self.calculate_worked_hour()
        user_presence.total_working_hours = self.calculate_total_working_hours()

        if is_created:
            user_presence.save()
        else:
            user_presence.save(
                update_fields=[
                    "enter_at",
                    "exit_at",
                    "work_start_time",
                    "work_end_time",
                    "present_time",
                    "total_working_hours",
                ]
            )

        return True


def recalculate_user_old_presences(user):
    """
    Recalculate user's old presences for the given month
    """
    user_presences = UserPresence.objects.filter(user=user, present_time=0).order_by("date")
    for user_presence in user_presences:
        UserDailyPresence(user, user_presence.date).store_daily_presence()
