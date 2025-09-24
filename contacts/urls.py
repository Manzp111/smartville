from django.urls import path
from .views import ContactListView, ContactCreateView, ContactDetailView

urlpatterns = [
    path("contacts/", ContactListView.as_view(), name="contact-list"),
    path("contacts/create/", ContactCreateView.as_view(), name="contact-create"),
    path("contacts/<uuid:pk>/", ContactDetailView.as_view(), name="contact-detail"),
]
