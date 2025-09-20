# visitor/pagination.py
from rest_framework.pagination import PageNumberPagination

class VisitorPagination(PageNumberPagination):
    page_size = 10          # default items per page
    page_size_query_param = 'limit'  # allow client to set limit
    max_page_size = 100
