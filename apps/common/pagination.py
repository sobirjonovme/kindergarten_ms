from rest_framework.pagination import LimitOffsetPagination


class CustomPagination100(LimitOffsetPagination):
    default_limit = 100
