import requests
from lib.api_clients.types import VideoStream, VideoListItem


class PipedClient:

    def __init__(self, instance_url):
        self._url = instance_url
        if not self._url.endswith("/"):
            self._url.append("/")

    def trending(self, region):
        response = self._request("trending", region=region).json()
        return self._json_to_VideoListItems(response)

    def video(self, video_id):
        response = self._request(f"streams/{video_id}").json()

        # search for dash manifest first
        manifest_type = "mpd"
        manifest_url = response.get("dash", None)
        if manifest_url is None:
            # search for hls manifest
            manifest_url = response.get("hls", None)
            manifest_type = "hls"
            if manifest_url is None:
                raise NotImplementedError("No manifest file found")

        return VideoStream(manifest_url, manifest_type)

    def search(self, query, region):
        response = self._request("search",
                                 q=query,
                                 filter="videos",
                                 region=region).json()

        return self._json_to_VideoListItems(response["items"])

    def _request(self, method, **params):
        full_url = self._url + method
        response = requests.get(full_url, params=params, timeout=5)

        response.raise_for_status()

        return response

    def _json_to_VideoListItems(self, response):
        videos = []

        for video in response:
            # Get a description (fallback to shortDescription if no description found)
            description = video.get("description",
                                    video.get("shortDescription", None))

            # currently /watch?v= is returned by Piped API
            video_id = video["url"].lstrip("/watch?v=")
            # Author is either in "uploaderName" or "uploader" field depending on request
            author = video.get("uploaderName", video.get("uploader", None))
            # build our VideoItem named tuple
            videos.append(
                VideoListItem(video_id, video["title"], author, description,
                              video["thumbnail"], video["duration"]))

        return videos
