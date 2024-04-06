from django.apps import AppConfig


# Configuration for the 'video_collection' app
class VideoCollectionConfig(AppConfig):
    # Set the default primary key field type
    default_auto_field = 'django.db.models.BigAutoField'
    # Set the name of the app
    name = 'video_collection'
