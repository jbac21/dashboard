
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("data", views.data, name="data"),
    path("datafields", views.datafields, name="datafields"),
    path("kpi", views.kpi, name="kpi"),
    path("delete_tile", views.delete_tile, name="delete_tile"),
    path("delete_data", views.delete_data, name="delete_data"),
    path("delete_pIndicator", views.delete_pIndicator, name="delete_pIndicator"),
    path("delete_df", views.delete_df, name="delete_df")
]
