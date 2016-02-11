import os.path
import shutil
import zipfile

import unittest

from pathlib import Path


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

        self.base_path = base_test_dir
        self.doc_path = doc_test_dir
        self.fin_path = fin_test_dir
        self.bank_path = bank_test_dir

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
    def testMakeSimpleArchive(self):
        file_path = os.path.join(self.fin_path, "testfile.txt")
        with open(file_path, "w") as fh:
            lines = ["toto", "test", "852.90$", "Truc"]
            fh.writelines(lines)

        zip_file_path = os.path.join(self.base_path, "test.zip")
        with zipfile.ZipFile(zip_file_path, mode="w") as my_zip:
            my_zip.write(file_path)

        self.assertTrue(os.path.exists(zip_file_path))

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


class MakeArchive:
    def create_with_dirs(self, dir_list):
        pass


if __name__ == "__main__":
    unittest.main()

