from django.shortcuts import render, redirect # used to render HTML templates with context data
from .models import Video
from .forms import VideoForm, SearchForm
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST


def home(request):
    app_name = 'Exercise Videos'
    return render(request, 'video_collection/home.html', {'app_name': app_name})


def add(request):
    if request.method == 'POST':  # adding a new video
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            try:
                new_video_form.save()  # Creates new Video object and saves
                return redirect('video_list')
            except IntegrityError:
                messages.warning(request, 'You already added that video')
            except ValidationError:
                messages.warning(request, 'Invalid YouTube URL')

        # Invalid form
        messages.warning(request, 'Check the data entered')
        return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})

    new_video_form = VideoForm()
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})


def video_list(request):
    search_form = SearchForm(request.GET)

    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term']
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name'))

    else:
        search_form = SearchForm()
        videos = Video.objects.order_by(Lower('name'))

    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form})


# Function responsible for deleting a video object from the database
# Decorator ensures that the view only responds to HTTP POST requests.
# It returns a 405 Method Not Allowed response for all other HTTP methods.
@require_POST
def delete_video(request, video_id):
    #  used to retrieve an object from the database based on the provided lookup parameters.
    #  If the object does not exist, it raises a 404 Http404 exception.
    video = get_object_or_404(Video, pk=video_id)
    video.delete()
    # Used to perform a redirect to a specified URL
    return redirect('video_list')