"""
give same basic capacities as zipFile.
archive
extract

password for both

archive will only accept list of folders.
"""

import os
import os.path
import shutil
import subprocess

from pathlib import Path

import unittest


class SevenZipFile:
    def __init__(self, file_path):
        self.path = file_path

    def archive_dirs(self, list_dirs, arcname, password):
        """
        rc = subprocess.call(['7z', 'a', '-pP4$$W0rd', '-y', 'myarchive.zip'] +
                     ['first_file.txt', 'second.file'])
        :param list_dirs:
        :param arcname:
        :param password:
        :return:
        """
        if password is None:
            password = "abc123$"
        if arcname is None:
            arcname = "seven"

        arc_file_name = arcname

        arcname = arcname.join(".7z")
        arcname = os.path(self.file_path, arcname)
        list_file_path = os.path(self.file_path, "list.txt")

        with open(list_file_path, "w") as fh:
            for a_dir in list_dirs:
                fh.write("\n".join(a_dir))

        res = subprocess.run(["7z", "a", "-p{pass}".format(password), "-mhe",
                               "@{list_path}".format(list_path=list_file_path)]).returncode

        if res != 0:
            return False
        else:
            return True


    def extract_all(self, file_path, extract_path, password):
        # make new file_path for ZIP inside extract path
        shutil.copy(file_path, extract_path)
        # use new path here.
        res = subprocess.run(["7z", "x", "{file}".format(file=file_path)]).returncode

        if res != 0:
            return False
        else:
            return True
