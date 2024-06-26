from django.urls import path

from . import views

app_xhatname = "model"
urlpatterns = [
    path("constituency/<str:constituency_id>/", views.constituency, name="constituency"),
    path("", views.index, name="main"),
]