from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from .models import Video


class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        # Test if the home page contains the expected title message
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Exercise Videos')


class TestAddVideos(TestCase):

    # Adding a video, added to DB and video_id created
    # Test adding a video
    def test_add_video(self):
        # Test adding a video and verifying its presence in the database and on the video list page
        # Prepare valid video data
        add_video_url = reverse('add_video')

        valid_video = {
            'name': 'yoga',
            'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
            'notes': 'yoga for neck and shoulders'
        }
        # Submit the form and follow redirects
        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video, follow=True)

        # Assertions to check if the video is added successfully
        # redirect to video list
        self.assertTemplateUsed('video_collection/video_list.html')

        # video list shows new video
        self.assertContains(response, 'yoga')
        self.assertContains(response, 'https://www.youtube.com/watch?v=4vTJHUDB5ak')
        self.assertContains(response, 'yoga for neck and shoulders')

        # video count on page is correct
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')  # and the non-plural form is used

        # one new video in the database
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        # get that video - if there's 1 video it must be the one added
        video = Video.objects.first()

        self.assertEqual('yoga', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=4vTJHUDB5ak', video.url)
        self.assertEqual('yoga for neck and shoulders', video.notes)
        self.assertEqual('4vTJHUDB5ak', video.video_id)

        # add another video - both present?

        valid_video_2 = {
            'name': 'full body workout',
            'url': 'https://www.youtube.com/watch?v=IFQmOZqvtWg',
            'notes': '30 minutes of aerobics'
        }

        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video_2, follow=True)

        # redirect to video list
        self.assertTemplateUsed('video_collection/video_list.html')

        # video count on page is correct
        self.assertContains(response, '2 videos')

        # video list shows both new videos

        # video 1,
        self.assertContains(response, 'yoga')
        self.assertContains(response, 'https://www.youtube.com/watch?v=4vTJHUDB5ak')
        self.assertContains(response, 'yoga for neck and shoulders')

        # and video 2
        self.assertContains(response, 'full body workout')
        self.assertContains(response, 'https://www.youtube.com/watch?v=IFQmOZqvtWg')
        self.assertContains(response, '30 minutes of aerobics')

        # database contains two videos
        self.assertEqual(2, Video.objects.count())

        # both video present on page? Another way to check is to query for a video with all the expected data.
        # the get method will raise a DoesNotExist error if a matching video is not found, and that will cause the test to fail

        video_1_in_db = Video.objects.get(name='yoga', url='https://www.youtube.com/watch?v=4vTJHUDB5ak', \
                                          notes='yoga for neck and shoulders', video_id='4vTJHUDB5ak')

        video_2_in_db = Video.objects.get(name='full body workout', url='https://www.youtube.com/watch?v=IFQmOZqvtWg', \
                                          notes='30 minutes of aerobics', video_id='IFQmOZqvtWg')

        # how about the correct videeos in the context?
        videos_in_context = list(response.context[
                                     'videos'])  # the object in the response is from a database query, so it's a QuerySet object. Convert to a list

        expected_videos_in_context = [video_2_in_db, video_1_in_db]  # in this order, because they'll be sorted by name
        self.assertEqual(expected_videos_in_context, videos_in_context)

    # Notes are optional
    # Test if a video can be added without notes
    def test_add_video_no_notes_video_added(self):
        # Test adding a video without notes and verify its presence in the database and on the video list page
        # (similar to the previous test but without notes)

        add_video_url = reverse('add_video')

        valid_video = {
            'name': 'yoga',
            'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
            # no notes
        }

        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video, follow=True)

        # redirect to video list
        self.assertTemplateUsed('video_collection/video_list.html')

        # video list shows new video
        self.assertContains(response, 'yoga')
        self.assertContains(response, 'https://www.youtube.com/watch?v=4vTJHUDB5ak')

        # video count on page is correct
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')  # and the non-plural form is used

        # one new video in the database
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        # get that video - if there's 1 video it must be the one added
        video = Video.objects.first()

        self.assertEqual('yoga', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=4vTJHUDB5ak', video.url)
        self.assertEqual('', video.notes)
        self.assertEqual('4vTJHUDB5ak', video.video_id)

    # Invalid videos not added
    # Test adding a video with missing fields
    def test_add_video_missing_fields(self):
        # Test adding a video with missing required fields and verify error messages
        # (checks if the form validation works correctly)
        add_video_url = reverse('add_video')

        invalid_videos = [
            {
                'name': '',  # no name, should not be allowed
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            },
            {
                # no name field
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            },
            {
                'name': 'example',
                'url': '',  # no URL, should not be allowed
                'notes': 'yoga for neck and shoulders'
            },
            {
                'name': 'example',
                # no URL
                'notes': 'yoga for neck and shoulders'
            },
            {
                # no name
                # no URL
                'notes': 'yoga for neck and shoulders'
            },
            {
                'name': '',  # blank - not allowed
                'url': '',  # no URL, should not be allowed
                'notes': 'yoga for neck and shoulders'
            },

        ]

        for invalid_video in invalid_videos:
            # follow=True not necessary because if video not valid, will expect a simple response
            response = self.client.post(add_video_url, data=invalid_video)

            self.assertTemplateUsed('video_collection/add_video.html')  # still on add page
            self.assertEqual(0, Video.objects.count())  # no video added to database
            messages = response.context['messages']  # get the messages
            message_texts = [message.message for message in messages]  # and the message texts
            self.assertIn('Check the data entered', message_texts)  # is this message one of the messages?

            # And we can also check that message is displayed on the page
            self.assertContains(response, 'Check the data entered')

    # Duplicates not allowed
    # Test adding a duplicate video
    def test_add_duplicate_video_not_added(self):
        # Test adding a duplicate video and verify that it's not added and appropriate messages are shown

        # Since an integrity error is raised, the database has to be rolled back to the state before this
        # action (here, adding a duplicate video) was attempted. This is a separate transaction so the
        # database might be in a weird state and future queries in this method can fail with atomic transaction errors.
        # the solution is to ensure the entire transation is in an atomic block so the attempted save and subsequent
        # rollback are completely finished before more DB transactions - like the count query - are attempted.

        # Most of this is handled automatically in a view function, but we have to deal with it here.

        with transaction.atomic():
            new_video = {
                'name': 'yoga',
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            }

            # Create a video with this data in the database
            # the ** syntax unpacks the dictonary and converts it into function arguments
            # https://python-reference.readthedocs.io/en/latest/docs/operators/dict_unpack.html
            # Video.objects.create(**new_video)
            # with the new_video dictionary above is equivalent to
            # Video.objects.create(name='yoga', url='https://www.youtube.com/watch?v=4vTJHUDB5ak', notes='for neck and shoulders')
            Video.objects.create(**new_video)

            video_count = Video.objects.count()
            self.assertEqual(1, video_count)

        with transaction.atomic():
            # try to create it again
            response = self.client.post(reverse('add_video'), data=new_video)

            # same template, the add form
            self.assertTemplateUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [message.message for message in messages]
            self.assertIn('You already added that video', message_texts)

            self.assertContains(response, 'You already added that video')  # and message displayed on page

        # still one video in the database
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

    # Test adding a video with an invalid URL
    def test_add_video_invalid_url_not_added(self):
        # Test adding a video with an invalid URL and verify that it's not added and appropriate messages are shown

        # what other invalid strings shouldn't be allowed?

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            '',
            '    sdfsdf sdfsdf   sfsdfsdf',
            '    https://minneapolis.edu?v=123456     ',
            '[',
            '☂️🌟🌷',
            '!@#$%^&*(',
            '//',
            'file://sdfsdf',
        ]

        for invalid_url in invalid_video_urls:
            new_video = {
                'name': 'yoga',
                'url': invalid_url,
                'notes': 'yoga for neck and shoulders'
            }

            response = self.client.post(reverse('add_video'), data=new_video)

            # same template, the add form
            self.assertTemplateUsed('video_collection/add.html')

            # Messages set correctly?
            messages = response.context['messages']
            message_texts = [message.message for message in messages]
            self.assertIn('Check the data entered', message_texts)
            self.assertIn('Invalid YouTube URL', message_texts)

            # and messages displayed on page
            self.assertContains(response, 'Check the data entered')
            self.assertContains(response, 'Invalid YouTube URL')

            # no videos in the database
            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):
    # Test cases related to the video list page
    # All videos shown on list page, sorted by name, case insensitive

    def test_all_videos_displayed_in_correct_order(self):
        # Test if all videos are displayed in the correct order on the video list page
        # (checks if videos are sorted alphabetically by name)
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v2, v4, v3, v1]
        response = self.client.get(reverse('video_list'))
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_no_video_message(self):
        # No video message
        # Test if a message is displayed when there are no videos
        # (checks if the correct message is displayed when the video list is empty)
        response = self.client.get(reverse('video_list'))
        videos_in_template = response.context['videos']
        self.assertContains(response, 'No videos.')
        self.assertEqual(0, len(videos_in_template))

    def test_video_number_message_single_video(self):
        # 1 video vs 4 videos message
        # Test if the correct message is displayed when there is only one video
        # (singular form of the message)
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')  # check this, because '1 videos' contains '1 video'

    def test_video_number_message_multiple_videos(self):
        # Test if the correct message is displayed when there are multiple videos
        # (plural form of the message)
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='uvw', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '4 videos')

    # search only shows matching videos, partial case-insensitive matches

    def test_video_search_matches(self):
        # Test if video search returns matching videos
        # (checks if search functionality works correctly)
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_video_search_no_matches(self):
        # Test if appropriate message is displayed when there are no search matches
        # (checks if the correct message is displayed when search yields no results)
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = []  # empty list
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No videos')


class TestVideoModel(TestCase):
    # Test cases related to the Video model

    def test_create_id(self):
        # Test if the video ID is correctly extracted from the URL and stored in the database
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        self.assertEqual('IODxDxX7oi4', video.video_id)

    def test_create_id_valid_url_with_time_parameter(self):
        # Test if the video ID extraction works with a valid URL containing additional parameters
        # a video that is playing and paused may have a timestamp in the query
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4&ts=14')
        self.assertEqual('IODxDxX7oi4', video.video_id)

    def test_create_video_notes_optional(self):
        # Test if a video can be created without notes
        v1 = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=67890')
        v2 = Video.objects.create(name='different example', notes='example',
                                  url='https://www.youtube.com/watch?v=12345')
        expected_videos = [v1, v2]
        database_videos = Video.objects.all()
        self.assertCountEqual(expected_videos,
                              database_videos)  # check contents of two lists/iterables but order doesn't matter.

    def test_invalid_urls_raise_validation_error(self):
        # Test if creating a video with an invalid URL raises a validation error
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://www.youtube.com/watch?v1234',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            ''
        ]

        for invalid_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='example', url=invalid_url, notes='example notes')

        video_count = Video.objects.count()
        self.assertEqual(0, video_count)

    def duplicate_video_raises_integrity_error(self):
        # Test if creating a duplicate video raises an integrity error
        Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')


class TestVideoDelete(TestCase):
    def setUp(self):
        # Create a test video object before running each test case
        self.video = Video.objects.create(name='Test Video', url='https://www.youtube.com/watch?v=R5xMzJe-NLQ&t=1s')

    def test_delete_video(self):
        # Test deleting an existing video
        # Get the initial count of videos
        initial_count = Video.objects.count()
        # Send a POST request to delete the video
        response = self.client.post(reverse('delete_video', args=[self.video.id]))
        # Check if the response is a redirect (HTTP status code 302)
        # Check for redirection
        self.assertEqual(response.status_code, 302)
        # Check if the video is deleted by verifying the count
        # Check if video is deleted
        self.assertEqual(Video.objects.count(), initial_count - 1)

    def test_delete_nonexistent_video(self):
        # Test attempting to delete a non-existent video
        # Get the initial count of videos
        initial_count = Video.objects.count()
        # Assuming there's no video with this ID
        nonexistent_id = self.video.id + 1
        # Send a POST request to delete a non-existent video
        response = self.client.post(reverse('delete_video', args=[nonexistent_id]))
        # Check if the response is a 404 Not Found
        self.assertEqual(response.status_code, 404)
        # Check if the video count remains unchanged after attempting deletion
        self.assertEqual(Video.objects.count(), initial_count)


class VideoDetailTestCase(TestCase):
    def setUp(self):
        # Create a sample video for testing
        self.video = Video.objects.create(
            name='Test Video',
            url='https://www.youtube.com/watch?v=ewow1NDSfKw',
            notes='This is a test video',
            video_id='test_id'
        )

    def test_video_detail_existing_video(self):
        # Get the URL for the video detail page for the existing video
        detail_url = reverse('video_list')

        # Issue a GET request to the detail URL
        response = self.client.get(detail_url)

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the response contains the video's information
        self.assertContains(response, self.video.name)
        self.assertContains(response, self.video.url)
        self.assertContains(response, self.video.notes)

    # def test_video_detail_nonexistent_video(self):
    #     # Get the URL for a non-existent video detail page
    #     detail_url = reverse('video_list')
    #     #
    #     # # Issue a GET request to the detail URL
    #     response = self.client.get(detail_url)
    #     #
    #     # # Check that the response status code is 404 (Not Found)
    #     self.assertEqual(response.status_code, 404)


