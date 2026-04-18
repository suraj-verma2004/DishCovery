from django.contrib import admin
from django.urls import path
from core import views
from django.urls import re_path

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('discover/', views.discover_view, name='discover'),
    path('compare/', views.compare_view, name='compare'),
    path('add/', views.add_restaurant, name='add_restaurant'),
    path('restaurant/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('update/<int:pk>/', views.update_restaurant, name='update_restaurant'),
    path('delete/<int:pk>/', views.delete_restaurant, name='delete_restaurant'),
    path('report/<int:pk>/', views.report_data, name='report_data'),
    path('restaurant/<int:pk>/rate/', views.submit_rating, name='submit_rating'), # New
    path('profile/', views.user_profile_view, name='user_profile'), 
    path('update-profile/', views.update_profile, name='update_profile'),
    path('profile/<str:username>/', views.user_profile_view, name='public_profile'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('community/', views.community_chat, name='community_chat'),
path('restaurant/<int:pk>/report/', views.report_restaurant, name='report_restaurant'),

]



