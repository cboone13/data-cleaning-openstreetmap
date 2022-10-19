#!/usr/bin/python
########################################################################
# Name: dataWranglingScript
#
# Description: Main script for using the audit.py and cleaning.py to audit
#              and clean data form a specified .osm file then load it into
#              a database.
#
# History:
# 05/23/2019    Christopher P. Boone     Genisis.
########################################################################
# Imports
import fullRun as OsmAudit
import configparser
import sys
# sys.path.append("./Data Wrangling with MongoDB")

CONFIG_FILE = 'dataWrangling_scripts.ini'


def get_config_data(configFile):
    """
    Method to get all data from a config file.
    """
    assert configFile, "Missing parameter!"

    try:
        config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())

        if not config.read(configFile):
            raise Exception("OSError", "File not found!")

        config_data = {}

        for section in config.sections():
            # Create an empty dictionary for each section
            config_data[section] = {}

            # Loop through pieces of the section
            for (key, val) in config.items(section):
                # Add the KEY : value pair
                config_data[section].update({key.upper(): val})

    except KeyError as err:
        err_msg = "{}:{} - Item {} not found in configuration file "\
                  "\"{}\".\n".format(__name__,
                                     "get_config_data()",
                                     err.args[0],
                                     configFile)
        # print("%s" % err_msg)
        raise Exception(err_msg)

    return config_data
########################################################################
#                              MAIN
########################################################################
if __name__ == '__main__':

    # Set up configuration.
    try:
        config_data = get_config_data(CONFIG_FILE)
    except:
        assert False, "Error in obtaining config data!"
        sys.exit(-1)

    # Perform audit
    PerformOsmAudit = OsmAudit.AuditClean(config_data)
    PerformOsmAudit.process()
    print('Process Complete')
    sys.exit(0)
