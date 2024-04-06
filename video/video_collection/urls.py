from django.urls import path
from . import views
from .views import delete_video

urlpatterns = [
    # URL pattern for the home page, mapped to the home view function
    path('', views.home, name='home'),
    # URL pattern for adding a new video, mapped to the add view function
    path('add', views.add, name='add_video'),
    # URL pattern for displaying the list of videos
    path('video_list', views.video_list, name='video_list'),
    # URL pattern for deleting a video by its ID
    path('video/<int:video_id>/delete/', delete_video, name='delete_video')
]
