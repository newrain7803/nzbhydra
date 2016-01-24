from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from future import standard_library

#standard_library.install_aliases()
from builtins import *
import logging

from nzbhydra import config
import requests
from furl import furl


logger = logging.getLogger('root')

currentVersion = None
currentVersionText = None


def versiontuple(v):
    filled = []
    for point in v.split("."):
        filled.append(point.zfill(8))
    return tuple(filled)


def check_for_new_version():
    new_version_available, new_version = is_new_version_available()
    if new_version_available:
        logger.info(("New version %s available at %s" % (new_version, config.mainSettings.repositoryBase.get())))


def get_rep_version():
    try:
        main_dir = os.path.dirname(os.path.dirname(__file__))
        
        if os.path.exists(os.path.join(main_dir, "nzbhydra.exe")):
            branch = "releases"
        else:
            branch = config.mainSettings.branch.get()
        url = furl(config.mainSettings.repositoryBase.get())
        url.host = "raw.%s" % url.host
        url.path.add(branch)
        url.path.add("version.txt")        
        
        logger.debug("Loading repository version from %s" % url)
        r = requests.get(url, verify=False)
        r.raise_for_status()
        return versiontuple(r.text), r.text
    except requests.RequestException as e:
        logger.error("Error downloading version.txt from %s to check new updates: %s" % (url, e))
        return None, None


def get_current_version():
    global currentVersion
    global currentVersionText
    if currentVersion is None:
        try:
            with open("version.txt", "r") as f:
                version = f.read()
            currentVersion = versiontuple(version)
            currentVersionText = version
            return currentVersion, currentVersionText
        except Exception as e:
            logger.error("Unable to open version.txt: %s" % e)
            return None, None
    return currentVersion, currentVersionText


def is_new_version_available():
    rep_version, rep_version_readable = get_rep_version()
    current_version, _ = get_current_version()
    try:
        if rep_version is not None and current_version is not None:
            return rep_version > current_version, rep_version_readable
    except Exception as e:
        logger.error("Error while comparion versions: %s" % e)
        return False, None
    return False, None
