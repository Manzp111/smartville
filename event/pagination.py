# event/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 1  # default items per page
    page_size_query_param = "page_size"  # client can override page size
    max_page_size = 100  # maximum items per page

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "message": "Data retrieved successfully",
            "next": bool(self.page.has_next()),
            "previous": bool(self.page.has_previous()),
            "next_link": self.get_next_link(),
            "previous_link": self.get_previous_link(),
            "count": self.page.paginator.count,
            "page_count": len(data),   
            "data": data
        })
