import ast
import copy
import datetime
import hashlib
import os
import re
import sys
import types
from configparser import NoOptionError, NoSectionError

sys.path.append(os.getcwd())


def ConfigSectionMap(Config, section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except (NoOptionError, NoSectionError):
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


def log(message):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + message)


def get_varnames_from_filenames(files):
    if isinstance(files[0], list):
        varnames = [os.path.basename(vname[0]).split("_")[0] for vname in files]
    else:
        varnames = os.path.basename(files[0]).split("_")[0]
    return varnames


def get_input_file_path(sect_dict, infolder):
    files2list = ast.literal_eval(sect_dict["in_files"])

    # Remove infolder='opendap', this is intended as a marker
    # and not a part of the path
    infolder = re.sub("opendap", "", infolder)

    if isinstance(files2list[0], list):
        sect_dict["in_files"] = [
            [os.path.join(infolder, f) for f in fil] for fil in files2list
        ]
    else:
        sect_dict["in_files"] = [os.path.join(infolder, f) for f in files2list]
    return sect_dict


def get_time_ranges(sect_dict):
    ts_names = ["dt1", "dt2", "base_dt1", "base_dt2"]
    for dt in ts_names:
        if dt in sect_dict.keys():
            if dt == "dt1":
                dt1 = datetime.datetime.strptime(sect_dict["dt1"], "%Y-%m-%d")
                dt2 = datetime.datetime.strptime(sect_dict["dt2"], "%Y-%m-%d")
                sect_dict["time_range"] = [dt1, dt2]
                del sect_dict["dt1"]
                del sect_dict["dt2"]

            elif dt == "base_dt1":
                base_dt1 = datetime.datetime.strptime(sect_dict["base_dt1"], "%Y-%m-%d")
                base_dt2 = datetime.datetime.strptime(sect_dict["base_dt2"], "%Y-%m-%d")
                sect_dict["base_period_time_range"] = [base_dt1, base_dt2]
                del sect_dict["base_dt1"]
                del sect_dict["base_dt2"]
    return sect_dict


def get_existing_entry(dic, entry):
    if entry in dic.keys():
        return dic[entry]
    else:
        return None


def flatten_list(nested_list):
    return [item for sublist in nested_list for item in sublist]


def get_cfg(args, Config, req_section, req_option):
    if getattr(args, req_option) == "None":
        if Config.has_section(req_section):
            option = Config.get(req_section, req_option)
        else:
            option = "opendap"  # Assume opendap
    else:
        option = getattr(args, req_option)
    return option


def make_string(non_string):
    if type(non_string) is dict:
        non_string = flatten_list(list(non_string.items()))
    elif isinstance(non_string, types.FunctionType):
        non_string = non_string.__name__
    elif isinstance(non_string, tuple):
        non_string = "".join(make_string(map(list, non_string)))
    elif isinstance(non_string, datetime.datetime):
        non_string = str(non_string)
    elif isinstance(non_string, float):
        non_string = str(non_string)
    elif isinstance(non_string, int):
        non_string = str(non_string)
    elif isinstance(non_string, list):
        non_string = "".join([make_string(item) for item in non_string])
    elif isinstance(non_string, bool):
        non_string = str(non_string)
    elif non_string is None:
        non_string = str(non_string)
    else:
        pass

    if type(non_string) is not str:
        non_string = make_string(non_string)

    return non_string


def get_test_md5hash(sect_dict, *args):
    sect_dict2 = copy.deepcopy(sect_dict)
    dict_keys_str = "".join(sect_dict2.keys())
    dict_values_str = "".join([make_string(item) for item in sect_dict2.values()])

    hashid = "".join(dict_values_str) + "".join(dict_keys_str) + "".join(args)
    hashid = hashlib.md5(hashid.encode("utf-8")).hexdigest()
    return hashid


def get_output_file_path(outfolder, section, sect_dict):
    testid = get_test_md5hash(sect_dict)

    outpath = os.path.join(outfolder, "_".join([section, "__TESTID_", testid + ".nc"]))
    sect_dict["out_file"] = outpath
    return sect_dict


def try_literal_interpretation(sect_dict, key):
    if key in sect_dict.keys():
        try:
            sect_dict[key] = ast.literal_eval(sect_dict[key])
        except ValueError:
            pass
    return sect_dict


def set_none_if_noneStr(sect_dict, key):
    if key in sect_dict.keys():
        if sect_dict[key] == "None":
            sect_dict[key] = None
    return sect_dict


def get_t_range_str(t_range, name):
    if t_range is not None:
        t1_str = t_range[0].strftime("%Y%m%d")
        t2_str = t_range[1].strftime("%Y%m%d")

        return "-".join([name, t1_str, t2_str])
    else:
        return ""


def get_suffix(in_files, dt_range, bt_range):
    suffix = ""
    dt_str = get_t_range_str(dt_range, "time_range")
    bt_str = get_t_range_str(bt_range, "base_period")

    if dt_str is not None:
        suffix = suffix + dt_str

    if bt_str is not None:
        suffix = suffix + bt_str

    if isinstance(in_files[0], list):
        suffix = re.sub(
            "[0-9]{8}-[0-9]{8}.nc$",
            suffix + ".nc",
            "_".join(os.path.basename(in_files[0][0]).split("_")[1:]),
        )
    else:
        suffix = re.sub(
            "[0-9]{8}-[0-9]{8}.nc$",
            suffix + ".nc",
            "_".join(os.path.basename(in_files[0]).split("_")[1:]),
        )
    return suffix
