#! /usr/bin/env python
import ast
import configparser
import logging
import os
from argparse import ArgumentParser

from auxiliary import (
    ConfigSectionMap,
    get_cfg,
    get_input_file_path,
    get_output_file_path,
    get_test_md5hash,
    get_time_ranges,
    get_varnames_from_filenames,
    try_literal_interpretation,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


# Check command arguments.
description = """icclim-test wrapper.py
Reads, parses and and executes test cases defined as Python config files"""

parser = ArgumentParser(description=description)
parser.add_argument(
    "-t",
    "--test-config",
    dest="testfiles",
    type=str,
    nargs="+",
    help="Test file or directory with the test cases in Python config format",
)
parser.add_argument(
    "-i",
    "--input",
    dest="input_test_data_dir",
    type=str,
    nargs="?",
    default="None",
    required=False,
    help="Folder for input test data files",
)
parser.add_argument(
    "-o",
    "--output",
    dest="test_output_dir",
    type=str,
    nargs="?",
    default="None",
    required=False,
    help="Output folder for test cases",
)
parser.add_argument(
    "-l",
    "--list-tests",
    action="store_true",
    dest="list_only",
    default=False,
    required=False,
    help="Only list tests, do not execute them",
)
args = parser.parse_args()

for files in args.testfiles:
    if os.path.isfile(files):
        files = [files]
    # Expand files if test dir given
    elif os.path.isdir(files):
        files = [os.path.join(files, file) for file in sorted(os.listdir(files))]
    else:
        raise ValueError(f"files is unexpected value: {files}")

    for file in files:
        config = configparser.ConfigParser()
        config.read(file)
        sections = [sec for sec in config.sections() if sec != "input_output"]

        # Use config file settings for input if not given on cmd-line
        input_test_data_dir = get_cfg(
            args, config, req_section="input_output", req_option="input_test_data_dir"
        )

        test_output_dir = get_cfg(
            args, config, req_section="input_output", req_option="test_output_dir"
        )

        # Create output folder
        if not os.path.exists(args.test_output_dir):
            os.mkdir(args.test_output_dir)

        # Loop sections in test config file
        for section in sections:
            ind = section.split("_")[0]
            logging.info("======> " + section)

            # Process some of the entries from the test config file
            section_dict = ConfigSectionMap(config, section)
            # section_dict = get_callback(section_dict)
            section_dict = get_input_file_path(section_dict, input_test_data_dir)
            section_dict = get_varnames_from_filenames(section_dict)
            section_dict = get_time_ranges(section_dict)
            section_dict = try_literal_interpretation(section_dict, "slice_mode")
            section_dict = try_literal_interpretation(section_dict, "threshold")

            if "user_indices" in section_dict.keys():
                section_dict["user_indices"] = ast.literal_eval(
                    section_dict["user_indices"]
                )

            testid = get_test_md5hash(section_dict, section, test_output_dir)
            section_dict = get_output_file_path(test_output_dir, section, section_dict)

            logging.info("Test ID: " + testid)

            # Run test
            if not args.list_only:
                import icclim.icclim

                icclim.icclim.index(**section_dict)
            logging.info("<====== " + section + "\n")
