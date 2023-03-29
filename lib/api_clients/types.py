from collections import namedtuple

VideoListItem = namedtuple(
    "VideoListItem",
    ["id", "title", "author", "description", "thumbnail_url", "duration"])

VideoStream = namedtuple("VideoStream", ["url", "type"])