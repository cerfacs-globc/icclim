import logging
import pkg_resources
import time
import os

os.environ['TZ'] = 'GMT'
time.tzset()
tz = time.tzname[0]

def start_message(tz=tz):

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

    logging.info("   ********************************************************************************************")
    logging.info("   *                                                                                          *")
    logging.info("   *          %-50s                V%-10s   *", 'icclim', pkg_resources.get_distribution("icclim").version)
    logging.info("   *                                                                                          *")
    logging.info("   *                                                                                          *")
    logging.info("   *          %-28s                                                    *", time.asctime(time.gmtime()) + " " + tz)
    logging.info("   *                                                                                          *")
    logging.info("   *          BEGIN EXECUTION                                                                 *")
    logging.info("   *                                                                                          *")
    logging.info("   ********************************************************************************************")

def wrong_variable_attribute_message(in_valid):
    if in_valid:
        logging.warning('   ********************************************************************************************')
        logging.warning('   *                                                                                          *')
        logging.warning('   *          CANNOT HANDLE variable attributes "valid_min", "valid_max", and "valid_range"   *') 
        logging.warning('   *                        values beyond these limits will be included in the computations   *')
        logging.warning('   *                        If present "missing_value" and/or "_FillValue" will be honoured   *')
        logging.warning('   *                                                                                          *')
        logging.warning('   ********************************************************************************************')

def ending_message(time_elapsed, tz=tz):
    

    logging.info("   ********************************************************************************************")
    logging.info("   *                                                                                          *")
    logging.info("   *          %-50s                V%-10s   *", 'icclim', pkg_resources.get_distribution("icclim").version)
    logging.info("   *                                                                                          *")
    logging.info("   *                                                                                          *")
    logging.info("   *          %-28s                                                    *", time.asctime(time.gmtime()) + " " + tz)
    logging.info("   *                                                                                          *")
    logging.info("   *          END EXECUTION                                                                   *")
    logging.info("   *                                                                                          *")
    logging.info("   *          CP SECS = %-10.3f                                                            *", time_elapsed)
    logging.info("   *                                                                                          *")
    logging.info("   ********************************************************************************************")
