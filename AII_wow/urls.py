#encoding:utf-8

from django.urls import path
from django.contrib import admin
from main import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index),
    path('populate/', views.populateDB),
    path('loadRS/', views.loadRS),
    path('whoosh-index/', views.whooshIndex),
    path('admin/', admin.site.urls),
    path('login/', views.login_view,name="login"),
    path('register/', views.register_view,name="register"),
    path("recommend/", views.recomendar_items),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("mis-items/", views.mis_items),
    path("add-item/", views.add_item),
    path("remove-item/", views.remove_item),
    path("search-name/", views.buscar_por_nombre),
    path("search-lvl/", views.buscar_por_nivel),
    path("search-keyword/", views.buscar_por_keyword),
    path("search-slot/", views.buscar_por_slot_tipo),
]