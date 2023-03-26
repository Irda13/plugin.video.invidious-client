from collections import namedtuple
import requests


class InvidiousClient:
    VideoListItem = namedtuple(
        "VideoListItem",
        ["id", "title", "author", "description", "thumbnail_url", "duration"])

    VideoStream = namedtuple("VideoStream", ["url"])

    def __init__(self, invidious_url):
        self._url = invidious_url + ("api/v1/" if invidious_url.endswith("/")
                                     else "/api/v1/")

    def trending(self, region):
        response = self._request("trending", region=region).json()
        return self._json_to_VideoListItems(response)

    def video(self, video_id):
        response = self._request(f"videos/{video_id[0]}").json()

        dash_url = response.get("dashUrl", None)
        if dash_url is None:
            raise NotImplemented("Only dash format is supported")

        return self.VideoStream(dash_url)

    def _request(self, method, **params):
        full_url = self._url + method
        response = requests.get(full_url, params=params, timeout=5)

        response.raise_for_status()

        return response

    def _json_to_VideoListItems(self, response):
        videos = []

        for video in response:
            if video["type"] in ["video", "shortVideo"
                                 ] and video["lengthSeconds"] > 0:
                # find a thumbnail
                thumbnail = self._get_thumbnail(video["videoThumbnails"])
                # Get a description
                description = video.get("description", None)
                if len(description) == 0:
                    description = None
                # build our VideoItem named tuple
                videos.append(
                    self.VideoListItem(video["videoId"], video["title"],
                                       video["author"], description, thumbnail,
                                       video["lengthSeconds"]))

        return videos

    def _get_thumbnail(self, thumbnails, quality="sddefault"):
        for thumb in thumbnails:
            # Search requested quality
            if thumb["quality"] == quality:
                return thumb["url"]
        # return 1st thumbnail if quality was not found
        return thumbnails[0]["url"]
