# utils/api_response.py
from rest_framework.response import Response
from urllib.parse import urlencode

def success_response(data=None, message="Success", status_code=200, pagination=None):
    """
    Standardized success response for all API endpoints with pagination support.
    """
    response_data = {
        "success": True,
        "message": message,
        "data": data
    }
    
    if pagination:
        response_data["pagination"] = pagination
        
    return Response(response_data, status=status_code)

def error_response(message="Error", errors=None, status_code=400):
    """
    Standardized error response for all API endpoints.
    """
    response_data = {
        "success": False,
        "message": message,
    }
    if errors is not None:
        response_data["errors"] = errors
    return Response(response_data, status=status_code)

def build_pagination_data(request, paginator, queryset):
    """
    Build pagination metadata for the response.
    """
    if not paginator:
        return None
        
    page = paginator.page
    return {
        "count": paginator.page.paginator.count,  # Total items
        "current_page": page.number,
        "total_pages": page.paginator.num_pages,
        "page_size": paginator.page_size,
        "next_page": page.has_next(),
        "previous_page": page.has_previous(),
        "next_page_url": _get_page_url(request, page.next_page_number()) if page.has_next() else None,
        "previous_page_url": _get_page_url(request, page.previous_page_number()) if page.has_previous() else None,
        "first_page_url": _get_page_url(request, 1),
        "last_page_url": _get_page_url(request, page.paginator.num_pages),
    }

def _get_page_url(request, page_number):
    """
    Generate URL for a specific page with all existing query parameters.
    """
    if not request:
        return None
        
    params = request.query_params.copy()
    params['page'] = page_number
    return f"{request.build_absolute_uri(request.path)}?{urlencode(params)}"