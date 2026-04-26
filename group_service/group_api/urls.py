from django.urls import path

from .views import group_members, groups_list_create, mark_presence


urlpatterns = [
    path("", groups_list_create),
    path("presence/", mark_presence),
    path("<int:group_id>/members/", group_members),
]
