import os

from MakeArchive import MakeArchive
from MakeArchive import ReadConfig


def execute():
    reader = ReadConfig("config.txt")
    dir_list = reader.read()
    print("zipping: {dirn}".format(dirn=dir_list[0]))
    make = MakeArchive()
    make.create_with_dirs(dir_list, os.getcwd(), r"F:\\test")

if __name__ == "__main__":
    execute()
