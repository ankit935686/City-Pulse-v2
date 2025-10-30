from django.urls import path
from . import views

urlpatterns = [
    path('', views.discussions_view, name='discussions'),
    path('create/', views.create_discussion, name='create_discussion'),
    path('<int:discussion_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:discussion_id>/comments/', views.get_comments, name='get_comments'),
    path('<int:discussion_id>/upvote/', views.toggle_upvote, name='toggle_upvote'),
    path('<int:discussion_id>/delete/', views.delete_discussion, name='delete_discussion'),
] 