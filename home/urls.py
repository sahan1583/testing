from django.contrib import admin
from django.urls import path, include
from home import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", views.index, name="index"),

    path("adminclick/", views.adminClick, name="adminclick"),
    path("adminlogin/", LoginView.as_view(template_name="admin_login.html"), name="adminlogin"),
    path("memberclick/", views.memberClick, name="memberclick"),
    path("membersignup/", views.memberSignup, name="membersignup"),
    path("memberlogin/", LoginView.as_view(template_name="member_login.html"), name="memberlogin"),
    path("logout/", LogoutView.as_view(template_name="home.html"), name="logout"),

    path("adminhome/", views.adminHome, name="adminhome"),
    path("memberhome/", views.memberHome, name="memberhome"),

    path("afterlogin/", views.afterlogin, name="afterlogin"),
    path("home", views.home, name="home"),
]
