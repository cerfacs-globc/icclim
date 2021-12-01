# flake8: noqa
# fmt: off
import logging
import os
import time
from enum import Enum

import pkg_resources

os.environ["TZ"] = "GMT"
time.tzset()
tz = time.tzname[0]


class Verbosity(Enum):
    LOW = ("LOW",)
    HIGH = ("HIGH",)
    NONE = ("NONE",)


def start_message(verbosity: Verbosity = Verbosity.HIGH):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    time_now = time.asctime(time.gmtime()) + " " + tz
    icclim_version = pkg_resources.get_distribution('icclim').version
    if verbosity == Verbosity.NONE:
        return
    if verbosity == Verbosity.LOW:
        logging.info(f"Icclim {icclim_version} --  {time_now}")
        logging.info("--- BEGIN EXECUTION ---")
        return
    logging.info("   ********************************************************************************************")
    logging.info("   *                                                                                          *")
    logging.info(f"   *          Icclim                {icclim_version}   *")
    logging.info("   *                                                                                          *")
    logging.info("   *                                                                                          *")
    logging.info(f"   *          {time_now}                                                    *")
    logging.info("   *                                                                                          *")
    logging.info("   *          BEGIN EXECUTION                                                                 *")
    logging.info("   *                                                                                          *")
    logging.info("   ********************************************************************************************")

def ending_message(time_cpu, tz=tz, verbosity: Verbosity = Verbosity.HIGH):
    time_now = time.asctime(time.gmtime()) + " " + tz
    icclim_version = pkg_resources.get_distribution('icclim').version
    if verbosity == Verbosity.NONE:
        return
    if verbosity == Verbosity.LOW:
        logging.info(f"Icclim {icclim_version} --  {time_now}")
        logging.info("CPU SECS = %-10.3f", time_cpu)
        logging.info("--- END EXECUTION ---")
        return
    logging.info("   ********************************************************************************************")
    logging.info("   *                                                                                          *")
    logging.info(f"   *          Icclim                {icclim_version}   *")
    logging.info("   *                                                                                          *")
    logging.info("   *                                                                                          *")
    logging.info(f"   *          {time_now}                                                    *")
    logging.info("   *                                                                                          *")
    logging.info("   *          END EXECUTION                                                                   *")
    logging.info("   *                                                                                          *")
    logging.info(f"   *          CP SECS = {time_cpu}                                                            *")
    logging.info("   *                                                                                          *")
    logging.info("   ********************************************************************************************")
