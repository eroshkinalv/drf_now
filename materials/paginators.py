from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    """
    Пагинатор для списка объектов Course
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class LessonPaginator(PageNumberPagination):
    """
    Пагинатор для списка объектов Lesson
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 1000
