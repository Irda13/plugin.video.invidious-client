import xbmcaddon
import xbmcgui
import xbmcplugin

from urllib.parse import urlencode, urlparse

from .router import Router
from lib.invidious_client import InvidiousClient

import inputstreamhelper


class InvidiousPlugin:

    def __init__(self, plugin_url, plugin_handle):
        self._plugin_handle = plugin_handle
        self._addon = xbmcaddon.Addon()

        # Init our router object with "main_menu" as default route
        self._router = Router(plugin_url, default_route="main_menu")

        # register our handlers
        self._router.register_route("main_menu", self.main_menu)
        self._router.register_route("trending", self.trending)
        self._router.register_route("play_video", self.play_video)

    def main_menu(self):
        # Trending list
        self._add_subdirectory("Trending", "trending")

        xbmcplugin.endOfDirectory(self._plugin_handle)

    def trending(self):
        client = self._get_client()
        videos = client.trending(region=self._get_setting("invidious_region"))

        self._display_videos(videos)
        xbmcplugin.endOfDirectory(self._plugin_handle)

    def play_video(self, video_id):
        # check if inputstream helper can handle protocol
        protocol = "mpd"
        input_stream_helper = inputstreamhelper.Helper(protocol)
        if not input_stream_helper.check_inputstream():
            raise RuntimeError(
                f"Cannot play video because Inpustream Helper does not support '{protocol}' protocol"
            )

        # perfor request
        client = self._get_client()
        video = client.video(video_id=video_id)
        # build list item from url
        play_item = xbmcgui.ListItem(path=video.url)
        play_item.setProperty("inputstream",
                              input_stream_helper.inputstream_addon)
        play_item.setProperty("inputstream.adaptive.manifest_type", protocol)
        xbmcplugin.setResolvedUrl(self._plugin_handle,
                                  succeeded=True,
                                  listitem=play_item)

    def run(self, query):
        # just route to the correct handler
        self._router.call(query)

    def _display_videos(self, videos):
        # create list items for videos
        for video in videos:
            # format title
            title = f"[B]{video.author}[/B] - {video.title}"
            list_item = xbmcgui.ListItem(title)

            list_item.setArt({"thumb": video.thumbnail_url})

            # Some videos have no description
            description = video.description if video.description else "No description available"

            # set info on listitem object
            list_item.setInfo(
                "video", {
                    "title": title,
                    "credits": video.author,
                    "plot": f"{title}\n\n{description}",
                    "duration": video.duration,
                    "mediatype": "video",
                })
            list_item.setProperty("IsPlayable", "true")

            # add the item to directory
            xbmcplugin.addDirectoryItem(self._plugin_handle,
                                        url=self._router.build_route(
                                            "play_video", video_id=video.id),
                                        listitem=list_item)

    def _get_client(self):
        return InvidiousClient(self._get_setting("invidious_instance_url"))

    def _get_setting(self, key):
        return xbmcplugin.getSetting(self._plugin_handle, key)

    def _get_addon_text(self, text_id):
        return self._addon.getLocalizedString(text_id)

    def _add_subdirectory(self, label, route, **args):
        list_item = xbmcgui.ListItem(label)
        xbmcplugin.addDirectoryItem(self._plugin_handle,
                                    url=self._router.build_route(
                                        route, **args),
                                    listitem=list_item,
                                    isFolder=True)
