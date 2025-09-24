# contacts/urls.py
from django.urls import path
from .views import ContactListView, ContactCreateView, ContactDetailView

urlpatterns = [
    path("", ContactListView.as_view(), name="contact-list"),          # Anyone can view
    path("create/", ContactCreateView.as_view(), name="contact-create"), # Leader only
    path("<uuid:pk>/", ContactDetailView.as_view(), name="contact-detail"), # Leader only
]
