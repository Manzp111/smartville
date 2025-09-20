from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size_query_param = "limit"  # allow ?limit=10
    max_page_size = 100

    def get_paginated_response(self, data):
        request = self.request
        paginator = self.page.paginator

        return Response({
            "success": True,
            "message": "Data retrieved successfully",
            "data": data,
            "meta": {
                "page": self.page.number,
                "limit": self.get_page_size(request),
                "total": paginator.count,
                "total_pages": paginator.num_pages,
                "has_next": self.page.has_next(),
                "has_prev": self.page.has_previous(),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            }
        })
