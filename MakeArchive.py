import os.path
import shutil
import zipfile

import unittest

from pathlib import Path

class TestMakeZip(unittest.TestCase):
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

    def testMakeSimpleArchive(self):
        file_path = os.path.join(self.fin_path, "testfile.txt")
        with open(file_path, "w") as fh:
            lines = ["toto", "test", "852.90$", "Truc"]
            fh.writelines(lines)

        zip_file_path = os.path.join(self.base_path, "test.zip")
        with zipfile.ZipFile(zip_file_path, mode="w") as my_zip:
            my_zip.write(file_path)

        self.assertTrue(os.path.exists(zip_file_path))


if __name__ == "__main__":
    unittest.main()

