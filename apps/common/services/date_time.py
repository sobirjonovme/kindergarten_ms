from django.utils import timezone


def find_diff_two_time(end_time, begin_time):
    """
    Find the difference between two times
    """
    if not end_time or not begin_time:
        return None

    end_time = timezone.datetime.combine(timezone.datetime.today(), end_time)
    begin_time = timezone.datetime.combine(timezone.datetime.today(), begin_time)

    diff = end_time - begin_time
    return diff


def get_last_month_date():
    today = timezone.localtime().date()
    last_month_date = today.replace(day=1) - timezone.timedelta(days=1)
    return last_month_date


def get_month_days_count(date):
    """
    Calculate the number of days in the given month
    """
    # List to hold the number of days in each month from January to December
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    year = date.year
    month = date.month

    # Check for leap year: Leap year if divisible by 4
    # Exception: years divisible by 100 are not leap years, unless also divisible by 400
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        month_days[1] = 29  # February gets an extra day in a leap year

    return month_days[month - 1]


def calculate_average_attendance(total_attendance, month_days_count, users_count):
    if not total_attendance or not users_count:
        return 0

    return total_attendance * 100 / (month_days_count * users_count)
