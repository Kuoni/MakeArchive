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


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        base_test_dir = os.path.join(os.getcwd(), "unittest") # be careful if modifying this line, check teardown rmtree.
        base_p = Path(base_test_dir)
        base_p.mkdir()
        dir_list = ["dir_one", "dir_two"]
        for the_dir in dir_list:
            dir_path = os.path.join(base_test_dir, the_dir)
            path_p = Path(dir_path)
            path_p.mkdir()

            with open(os.path.join(dir_path, "test.txt"), "w") as fh:
                fh.write("test")

        self.base_path = base_test_dir
        self.dir_list = dir_list

    def tearDown(self):
        shutil.rmtree(self.base_path)


class TestSevenZip(BaseTestCase):
    def testMakeSimpleZipWithFileList(self):
        root_zip_file_path = self.base_path
        s_zip = SevenZipFile(root_zip_file_path)
        dir_list = []
        for a_dir in self.dir_list:
            dir_list.append(os.path.join(self.base_path, a_dir))

        ret = s_zip.archive_dirs(dir_list, "test")
        self.assertTrue(ret)

        zip_filename_and_path = os.path.join(root_zip_file_path, "test.7z")
        self.assertTrue(os.path.exists(zip_filename_and_path))

    def testSimpleZipAndExtract(self):
        root_zip_file_path = self.base_path
        s_zip = SevenZipFile(root_zip_file_path)
        dir_list = []
        for a_dir in self.dir_list:
            dir_list.append(os.path.join(self.base_path, a_dir))

        ret = s_zip.archive_dirs(dir_list, "test")
        self.assertTrue(ret)

        zip_filename_and_path = os.path.join(root_zip_file_path, "test.7z")
        self.assertTrue(os.path.exists(zip_filename_and_path))

        extract_path = os.path.join(self.base_path, "dest")
        extract_p = Path(extract_path)
        extract_p.mkdir()
        eret = s_zip.extract_all(zip_filename_and_path, extract_path)
        self.assertTrue(eret)
        dirs_in_dir = os.listdir(extract_path)
        only_dir_list = []
        for a_dir in dirs_in_dir:
            if os.path.isdir(os.path.join(extract_path, a_dir)):
                only_dir_list.append(a_dir)

        self.assertEqual(2, len(only_dir_list))

    def testSimpleArchiveWithPassword(self):
        pass

    def testSimpleExtractWithPassword(self):
        pass


class SevenZipFile:
    def __init__(self, file_path):
        self.seven_path = r"C:\Program Files\7-Zip\7z.exe" #not gonna work if I need it to run on multiple machines.
        self.path = file_path
        self._password = None

    def set_pwd(self, pwd_str):
        self._password = pwd_str

    def archive_dirs(self, list_dirs, arcname, is_use_pwd=False):
        """
        :param list_dirs: a list of full or relative directory paths. directories ONLY.
        :param arcname: archive name
        :param is_use_pwd: should 7z be called with passw to archive with password.
        :return: True if command call was successful.
        """
        password = None
        if is_use_pwd:
            if self._password is None:
                password = "abc123$"
            else:
                password = self._password

        if arcname is None:
            arcname = "seven"

        arc_file_name = arcname + ".7z"
        arcname = os.path.join(self.path, arc_file_name)
        list_file_path = os.path.join(self.path, "list.txt")

        with open(list_file_path, "w") as fh:
            for a_dir in list_dirs:
                fh.write("{path}\n".format(path=a_dir))

        cmd_list = [self.seven_path, "a", arcname]
        if is_use_pwd:
            cmd_list.extend(["-p{pass}".format(password), "-mhe"])
        res = subprocess.run(cmd_list + [
                               "@{list_path}".format(list_path=list_file_path)]).returncode

        if res != 0:
            return False
        else:
            return True

    def extract_all(self, file_path, extract_path):
        """

        :param file_path:
        :param extract_path:
        :return:
        """
        # make new file_path for ZIP inside extract path
        shutil.copy(file_path, extract_path)
        # use new path here.
        filename = os.path.split(file_path)[1]
        full_extract_file_path = os.path.join(extract_path, filename)
        res = subprocess.run([self.seven_path, "x", "{file}".format(file=full_extract_file_path),
                              "-o{out_path}".format(out_path=extract_path)]).returncode

        if res != 0:
            return False
        else:
            return True
