import argparse
import os

from MakeArchive import MakeArchive
from MakeArchive import ReadConfig


def execute(conf_file_path):
    reader = ReadConfig(conf_file_path)
    dir_list = reader.read()
    
    make = MakeArchive(None)
    make.create_with_dirs(dir_list, os.getcwd(), r"F:\\test")

if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser(
        description="Copies folder given in a config list and zips them together finally" +
                    " it copies the zip to a final destination.")
    arg_parse.add_argument("-c", "--config", dest="config", default="config.txt",
                           help="specify this flag if you want to have the config read from somewhere else.")
    # make a killswitch switched on by default to disable emails
    # add a password file.
    the_args = arg_parse.parse_args()
    execute(the_args.config)
