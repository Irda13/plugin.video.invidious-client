import sys

from lib import Plugin


def main():
    # get plugin kodi url (plugin:// url)
    plugin_url = sys.argv[0]
    # get plugin handle as integer
    plugin_handle = int(sys.argv[1])
    # instanciate our plugin object
    plugin = Plugin(plugin_url, plugin_handle)
    # run plugin with args
    plugin_args = sys.argv[2]
    plugin.run(plugin_args)


if __name__ == "__main__":
    main()
