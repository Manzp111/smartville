from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'count': self.page.paginator.count,
            'meta': {
                'page': self.page.number,
                'limit': self.page_size,
                'total': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_prev': self.page.has_previous(),
            },
            'data': data
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                    'example': 'success'
                },
                'count': {
                    'type': 'integer',
                    'example': 123
                },
                'meta': {
                    'type': 'object',
                    'properties': {
                        'page': {'type': 'integer', 'example': 2},
                        'limit': {'type': 'integer', 'example': 10},
                        'total': {'type': 'integer', 'example': 45},
                        'total_pages': {'type': 'integer', 'example': 5},
                        'has_next': {'type': 'boolean', 'example': True},
                        'has_prev': {'type': 'boolean', 'example': True},
                    }
                },
                'data': schema,
            },
        }