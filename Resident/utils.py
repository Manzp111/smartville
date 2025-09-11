# account/utils.py

from Resident.models import Resident

def get_resident_location(user):
    """
    Returns the Location object associated with the logged-in user.
    """
    try:
        resident = Resident.objects.get(person=user.person, has_account=True, is_deleted=False)
        return resident.location
    except Resident.DoesNotExist:
        return None
