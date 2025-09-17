# Resident/utils.py
from django.contrib.auth.models import AnonymousUser

def get_resident_location(user):
    """
    Get the village location for a user, handling AnonymousUser
    """
    # Return None for AnonymousUser or unauthenticated users
    if not user.is_authenticated or isinstance(user, AnonymousUser):
        return None
    
    try:
        from .models import Resident  # Import here to avoid circular imports
        resident = Resident.objects.get(person__user=user, is_deleted=False)
        return resident.village
    except Resident.DoesNotExist:
        return None