from django.urls import path
from .views import groups_list_create, add_member

urlpatterns = [
    path("", groups_list_create),
    path("<int:group_id>/members/", add_member),
]