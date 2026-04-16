from django.urls import path

from .views import add_member, groups_list_create


urlpatterns = [
    path("", groups_list_create),
    path("<int:group_id>/members/", add_member),
]
