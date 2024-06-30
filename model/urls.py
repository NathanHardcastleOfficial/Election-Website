from django.urls import path

from . import views

app_name = "model"
urlpatterns = [
    path("constituency/<str:constituency_id>/", views.constituency, name="constituency"),
    path("addresults/", views.addResults, name="addresults"),
    path("", views.index, name="main"),
]