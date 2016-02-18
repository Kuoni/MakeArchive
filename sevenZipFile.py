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
import re

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
        for only_dir in only_dir_list:
            dir_path = os.path.join(extract_path, only_dir)
            file_path = os.path.join(dir_path, "test.txt")
            self.assertTrue(os.path.exists(file_path))

    def testSimpleArchiveWithPassword(self):
        root_zip_file_path = self.base_path
        s_zip = SevenZipFile(root_zip_file_path)
        dir_list = []
        for a_dir in self.dir_list:
            dir_list.append(os.path.join(self.base_path, a_dir))

        s_zip.set_pwd("abc123%")
        ret = s_zip.archive_dirs(dir_list, "test", True)
        self.assertTrue(ret)

        zip_filename_and_path = os.path.join(root_zip_file_path, "test.7z")
        self.assertTrue(os.path.exists(zip_filename_and_path))

    def testSimpleExtractWithPassword(self):
        root_zip_file_path = self.base_path
        s_zip = SevenZipFile(root_zip_file_path)
        dir_list = []
        for a_dir in self.dir_list:
            dir_list.append(os.path.join(self.base_path, a_dir))

        s_zip.set_pwd("abc123%$")
        ret = s_zip.archive_dirs(dir_list, "test", True)
        self.assertTrue(ret)
        s_zip.set_pwd("none")

        zip_filename_and_path = os.path.join(root_zip_file_path, "test.7z")
        self.assertTrue(os.path.exists(zip_filename_and_path))

        extract_path = os.path.join(self.base_path, "dest")
        extract_p = Path(extract_path)
        extract_p.mkdir()
        eret = s_zip.extract_all(zip_filename_and_path, extract_path, True)
        self.assertFalse(eret)

        s_zip.set_pwd("abc123%$")
        eret = s_zip.extract_all(zip_filename_and_path, extract_path, True)
        self.assertTrue(eret)
        dirs_in_dir = os.listdir(extract_path)
        only_dir_list = []
        for a_dir in dirs_in_dir:
            if os.path.isdir(os.path.join(extract_path, a_dir)):
                only_dir_list.append(a_dir)

        self.assertEqual(2, len(only_dir_list))
        for only_dir in only_dir_list:
            dir_path = os.path.join(extract_path, only_dir)
            file_path = os.path.join(dir_path, "test.txt")
            self.assertTrue(os.path.exists(file_path))

    def testZipInfoFilesAndFolders(self):
        root_zip_file_path = self.base_path
        s_zip = SevenZipFile(root_zip_file_path)
        dir_list = []
        for a_dir in self.dir_list:
            dir_list.append(os.path.join(self.base_path, a_dir))

        ret = s_zip.archive_dirs(dir_list, "test")
        self.assertTrue(ret)

        zip_filename_and_path = os.path.join(root_zip_file_path, "test.7z")
        self.assertTrue(os.path.exists(zip_filename_and_path))

        files, folders = s_zip.archive_info(zip_filename_and_path)
        self.assertEqual(2, files)
        self.assertEqual(2, folders)


class SevenZipFile:
    def __init__(self, file_path):
        self.seven_path = r"7z.exe"
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
            cmd_list.extend(["-p{pwd}".format(pwd=password), "-mhe"])
        res = subprocess.run(cmd_list + [
                               "@{list_path}".format(list_path=list_file_path)]).returncode

        if res != 0:
            return False
        else:
            return True

    def extract_all(self, file_path, extract_path, is_use_pwd=False):
        """
        Extracts all files from a 7z.
        :param file_path: full path to the 7z file.
        :param extract_path: directory path in which to extract.
        :param is_use_pwd: Boolean, are we using a password?
        :return: True if success, False otherwise.
        """
        if not os.path.exists(extract_path):
            os.mkdir(extract_path)

        # make new file_path for ZIP inside extract path
        shutil.copy(file_path, extract_path)
        # use new path here.
        filename = os.path.split(file_path)[1]
        full_extract_file_path = os.path.join(extract_path, filename)
        cmd_list = [self.seven_path, "x", "{file}".format(file=full_extract_file_path),
                    "-o{out_path}".format(out_path=extract_path)]
        if is_use_pwd:
            cmd_list.append("-p{pwd}".format(pwd=self._password))
        try:
            res = subprocess.run(cmd_list, timeout=10).returncode
        except TimeoutError:
            res = -1

        if res != 0:
            return False
        else:
            return True

    def archive_info(self, zip_file_path):
        """
        Returns the number of files and folders in the archive based on the 7z list function.
        :param zip_file_path: full path to zip file.
        :return: tuple: files first, folders second.
        """
        cmd_list = [self.seven_path, "l", zip_file_path]
        files_count = 0
        folders_count = 0
        try:
            res_dict = subprocess.run(cmd_list, timeout=10,stdout=subprocess.PIPE)
            res = res_dict.returncode
            data_str = str(res_dict.stdout)
            str_list = data_str.split('\\r\\n')
            last_str = str_list[-2]
            result = re.search("(\d+) files,\s+(\d+) folders", last_str)

            if result:
                files_count = int(result.groups()[0])
                folders_count = int(result.groups()[1])
        except TimeoutError:
            files_count = folders_count = 0

        return files_count, folders_count
