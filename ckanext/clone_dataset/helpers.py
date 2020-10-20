import logging

from ckan.model import Session
from ckan.model.package import Package
from pprint import pformat

log = logging.getLogger(__name__)


def get_package_start_with_name(start_with):
    u"""
    Return a list of package with name start with start_with.
    """
    try:
        return Session.query(Package).filter(Package.name.like(start_with + '-%')).all()
    except Exception as e:
        log.error(str(e))
        return []


def get_incremental_package_name(name):
    u"""
    Return a unique name for package, if there is a same name, use incremental value at the end of the name.
    """
    packages = get_package_start_with_name(name)
    titles = [package.name for package in packages]

    # If no duplicate name, return the name.
    package = Session.query(Package).filter(Package.name == name).all()
    if len(package) == 0:
        return name

    # If there is a duplicate, get incremental name.
    i = 1
    name_exist = True
    incremental_name = name
    while name_exist:
        incremental_name = name + '-' + str(i)
        name_exist = incremental_name in titles
        i += 1

    return incremental_name
