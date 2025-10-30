from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [  
    path('projects/', views.projects_overview, name='projects_overview'),
    path('officials/', views.officials_dashboard, name='officials_dashboard'),
    path('officials/trends/', views.trends_analysis, name='trends_analysis'),
    path('officials/bottlenecks/', views.bottlenecks_view, name='bottlenecks_view'),
    path('officials/road-analytics/', views.road_development_analytics, name='road_development_analytics'),
    path('api/projects/', views.get_projects_data, name='get_projects_data'),
    path('api/projects/filter/', views.filter_projects, name='filter_projects'),
    path('api/projects/load-csv/', views.load_csv_data, name='load_csv_data'),
    path('api/trends/', views.get_trends_data, name='get_trends_data'),
    path('api/bottlenecks/', views.get_bottlenecks_data, name='get_bottlenecks_data'),
    path('api/road-development/', views.get_road_development_data, name='get_road_development_data'),
    path('api/road-development/load-csv/', views.load_road_development_csv, name='load_road_development_csv'),
    path('api/bottlenecks/load-csv/', views.load_bottlenecks_csv, name='load_bottlenecks_csv'),
    path('api/metro/load-csv/', views.load_metro_csv, name='load_metro_csv'),
]

