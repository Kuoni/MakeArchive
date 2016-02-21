import datetime
import os.path
import shutil

import unittest

from pathlib import Path
from sevenZipFile import SevenZipFile


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        base_test_dir = os.path.join(os.getcwd(), "unittest") # be careful if modifying this line, check teardown rmtree.
        base_p = Path(base_test_dir)
        base_p.mkdir()
        doc_test_dir = os.path.join(base_test_dir, "Doc")
        doc_p = Path(doc_test_dir)
        doc_p.mkdir()
        fin_test_dir = os.path.join(doc_test_dir, "Fin")
        fin_p = Path(fin_test_dir)
        fin_p.mkdir()
        bank_test_dir = os.path.join(doc_test_dir, "Bank")
        bank_p = Path(bank_test_dir)
        bank_p.mkdir()
        other_fin_dir = os.path.join(base_test_dir, "Fin")
        other_fin_p = Path(other_fin_dir)
        other_fin_p.mkdir()

        self.base_path = base_test_dir
        self.doc_path = doc_test_dir
        self.fin_path = fin_test_dir
        self.bank_path = bank_test_dir
        self.other_fin_path = other_fin_dir

    def tearDown(self):
        shutil.rmtree(self.base_path)


class TestReadConfig(BaseTestCase):
    def testParse(self):
        lines = [self.fin_path, self.bank_path]
        conf_path = os.path.join(self.base_path, "config.txt")
        with open(conf_path, "w") as fh:
            fh.write("\n".join(lines))

        reader = ReadConfig(conf_path)
        paths = reader.read()
        self.assertEqual(2, len(paths))
        self.assertTrue(self.fin_path in paths)
        self.assertTrue(self.bank_path in paths)
        for path in paths:
            self.assertTrue(os.path.exists(path))


class TestMakeZip(BaseTestCase):

    def testMakeSimpleArchiveZipDir(self):
        file_path = os.path.join(self.fin_path, "testfile.txt")
        with open(file_path, "w") as fh:
            lines = ["toto", "test", "852.90$", "Truc"]
            fh.writelines(lines)

        s_zip = SevenZipFile(self.base_path)
        zip_file_path = os.path.join(self.base_path, "test.7z")
        ret = s_zip.archive_dirs([self.fin_path], "test")
        self.assertTrue(ret)
        self.assertTrue(os.path.exists(zip_file_path))

        unzip_path = os.path.join(self.base_path, "unzip")
        s_zip.extract_all(zip_file_path, unzip_path)
        another_list = os.listdir(unzip_path)
        self.assertEqual(2, len(another_list))
        fin_dir_found = False
        for root, dirs, files in os.walk(unzip_path):
            dirname = os.path.split(root)[1]
            if dirname == "Fin":
                fin_dir_found = True
                self.assertEqual(1, len(files))
                self.assertEqual(files[0], "testfile.txt")
        self.assertTrue(fin_dir_found)

    def testCopyFolders(self):
        """
        Simple, copies two folders with each one having a file and verifies that both folders and their file are copied.
        :return:
        """
        folders = [self.fin_path, self.bank_path]
        for folder in folders:
            file_path = os.path.join(folder, "testfile.doc")
            with open(file_path, "w") as fh:
                fh.write("test")

        dest_dir_p = Path(self.base_path, "dest")
        dest_dir_p.mkdir()

        for folder in folders:
            dirname = os.path.split(folder)[1]
            to_copy_dir_dest_p = dest_dir_p.joinpath(dirname)
            shutil.copytree(folder, str(to_copy_dir_dest_p))

        folder_list = os.listdir(str(dest_dir_p))

        for folder in folders:
            dirname = os.path.split(folder)[1]
            self.assertTrue(dirname in folder_list)
            file_path = os.path.join(str(dest_dir_p), dirname, "testfile.doc")
            self.assertTrue(os.path.exists(file_path))

    def testCopyFoldersConflict(self):
        """
        Test copytree duplicate error management when two folders from two different drives have the same name.
        :return:
        """
        folders = [self.fin_path, self.bank_path, self.other_fin_path]
        for folder in folders:
            file_path = os.path.join(folder, "testfile.doc")
            with open(file_path, "w") as fh:
                fh.write("test")

        make = MakeArchive(None)
        final_dest_p = Path(self.base_path, "final_dest")
        final_dest_p.mkdir()
        final_dest_path = str(final_dest_p)

        make.create_with_dirs([self.fin_path, self.bank_path, self.other_fin_path],
                              self.base_path, final_dest_path)
        dir_list = os.listdir(final_dest_path)
        dir_found_dict = {"Fin" : False, "Bank" : False, "unittest_Fin": False}

        for file in dir_list:
            ext = os.path.splitext(file)[1]
            if ext == ".7z":
                unzip_path = os.path.join(self.base_path, "unzip")
                zip_file_path = os.path.join(final_dest_path, file)
                s_zip = SevenZipFile(zip_file_path)
                ret = s_zip.extract_all(zip_file_path, unzip_path)
                self.assertTrue(ret)
                another_list = os.listdir(unzip_path)
                self.assertEqual(1+len(folders), len(another_list))
                for root, dirs, files in os.walk(unzip_path):
                    dirname = os.path.split(root)[1]
                    if dirname == "Fin" or dirname == "Bank" or dirname == "unittest_Fin":
                        dir_found_dict[dirname] = True
                        self.assertEqual(1, len(files))
                        for doc_file in files:
                            self.assertEqual("testfile.doc", doc_file)
            else:
                self.assertFalse(True)

            self.assertTrue(dir_found_dict["Fin"])
            self.assertTrue(dir_found_dict["Bank"])
            self.assertTrue(dir_found_dict["unittest_Fin"])

    def testFullMake(self):
        folders = [self.fin_path, self.bank_path]
        for folder in folders:
            file_path = os.path.join(folder, "testfile.doc")
            with open(file_path, "w") as fh:
                fh.write("test")

        make = MakeArchive(None)
        final_dest_p = Path(self.base_path, "final_dest")
        final_dest_p.mkdir()
        final_dest_path = str(final_dest_p)

        make.create_with_dirs([self.fin_path, self.bank_path], self.base_path, final_dest_path)
        dir_list = os.listdir(final_dest_path)
        dir_found_dict = {"Fin" : False, "Bank" : False}

        for file in dir_list:
            ext = os.path.splitext(file)[1]
            if ext == ".7z":
                unzip_path = os.path.join(self.base_path, "unzip")
                zip_file_path = os.path.join(final_dest_path, file)
                s_zip = SevenZipFile(zip_file_path)
                ret = s_zip.extract_all(zip_file_path, unzip_path)
                self.assertTrue(ret)
                another_list = os.listdir(unzip_path)
                self.assertEqual(1+len(folders), len(another_list))
                for root, dirs, files in os.walk(unzip_path):
                    dirname = os.path.split(root)[1]
                    if dirname == "Fin" or dirname == "Bank":
                        dir_found_dict[dirname] = True
                        self.assertEqual(1, len(files))
                        for doc_file in files:
                            self.assertEqual("testfile.doc", doc_file)
            else:
                self.assertFalse(True)

            self.assertTrue(dir_found_dict["Fin"])
            self.assertTrue(dir_found_dict["Bank"])


class ReadConfig:
    def __init__(self, conf_path):
        self.file_path = conf_path

    def read(self):
        res_list = []
        with open(self.file_path, "r") as fh:
            lines = fh.readlines()
            for line in lines:
                res_list.append(line.strip())

        return res_list


class DirectoryNotFoundError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class DirectoryConflictError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class CleanUpError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class MakeArchive:
    def __init__(self, pwd):
        self._password = pwd

    def create_with_dirs(self, dir_list, work_folder_path, copy_zip_to_path):
        if not os.path.exists(work_folder_path):
            raise DirectoryNotFoundError("work folder doesn't exist, it needs to exist so we can copy files.")
        if not os.path.exists(copy_zip_to_path):
            raise DirectoryNotFoundError("Final folder path doesn't exist.")
        if not os.path.isdir(copy_zip_to_path):
            raise NotADirectoryError("copy to path is not a directory")

        dest_root_path = os.path.join(work_folder_path, "work_temp")  # be careful with that line, a rmtree will be done on it.
        dest_dir_p = Path(dest_root_path)
        dest_dir_p.mkdir()

        dest_dir_list = []
        for folder in dir_list:
            split_path = os.path.split(folder)
            dirname = split_path[1]
            to_copy_dir_dest_p = dest_dir_p.joinpath(dirname)
            if os.path.exists(str(to_copy_dir_dest_p)):
                parent_dirname = os.path.split(split_path[0])[1]
                to_copy_dir_dest_p = dest_dir_p.joinpath(parent_dirname + "_" + dirname)
                if os.path.exists(str(to_copy_dir_dest_p)):
                    raise DirectoryConflictError("Cannot find a proper name for {folder}".format(folder=dirname))
            try:
                shutil.copytree(folder, str(to_copy_dir_dest_p))  # can throw Error
            except shutil.Error:
                raise DirectoryConflictError("Error during copy for folder: {dirname}".format(
                    dirname=dirname
                ))

            dest_dir_list.append(str(to_copy_dir_dest_p))

        timestamp = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
        archive_name = "backup_{stamp}".format(stamp=timestamp)
        zip_file_path = os.path.join(dest_root_path, archive_name + ".7z")
        s_zip = SevenZipFile(dest_root_path)
        is_use_pwd = False
        if self._password is not None:
            is_use_pwd = True
            s_zip.set_pwd(self._password)

        s_zip.archive_dirs(dest_dir_list, archive_name, is_use_pwd)

        shutil.copy(zip_file_path, copy_zip_to_path)
        files = 0
        folders = 0
        try:
            files, folders = s_zip.archive_info(zip_file_path, is_use_pwd)
        except Exception:
            files = folders = -1

        try:
            shutil.rmtree(dest_root_path)
        except PermissionError as ex:
            raise CleanUpError("Couldn't remove work folder.") from ex

        return files, folders


if __name__ == "__main__":
    unittest.main()

