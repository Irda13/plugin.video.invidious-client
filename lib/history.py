import xbmcvfs
import os

import xbmc


class HistoryFile:

    def __init__(self, xbmc_addon, file_name, max_entries, subfolders=None):
        path = xbmcvfs.translatePath(xbmc_addon.getAddonInfo('profile'))
        if subfolders:
            path = os.path.join(path, subfolders)
        if not os.path.exists(path):
            os.makedirs(path)
        self._file_name = os.path.join(path, file_name)

        self._max_entries = max_entries

    @property
    def entries(self):
        try:
            with xbmcvfs.File(self._file_name, "r") as f:
                return f.read().splitlines()
        except FileNotFoundError:
            return []

    def add_entry(self, new_entry):
        entries = self.entries
        # insert our entry at the begining
        entries.insert(0, new_entry)
        with xbmcvfs.File(self._file_name, "w+") as f:
            # this will write at most max_entries
            f.write("\n".join(entries[:self._max_entries]))
