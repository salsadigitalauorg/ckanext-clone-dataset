import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
import datetime

from flask import Blueprint
from ckanext.clone_dataset.helpers import get_incremental_package_name
from ckanext.clone_dataset.interfaces import IClone

log = logging.getLogger(__name__)
h = toolkit.h
request = toolkit.request
NotAuthorized = toolkit.NotAuthorized
get_action = toolkit.get_action
check_access = toolkit.check_access

clone_dataset = Blueprint('clone_dataset', __name__)


def clone(id):
    # Get current dataset.
    try:
        # Need to set the user info in the context for check_access
        context = {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        dataset_dict = get_action('package_show')(context.copy(), {'id': id})
        # Check the user has permission to clone the dataset
        check_access('package_create', context.copy(), dataset_dict)
    except NotAuthorized as e:
        log.error(str(e))
        h.flash_error(str(e))
        return h.redirect_to('/dataset')
    except Exception as e:
        log.error('Error loading dataset. id:%s' % id)
        h.flash_error('Error loading dataset. {0}'.format(str(e)))
        return h.redirect_to('/dataset')

    # Update necessary fields.
    dt = datetime.datetime.now(datetime.UTC).isoformat()
    dataset_dict['title'] = 'COPY of - ' + dataset_dict['title']
    dataset_dict['metadata_created'] = dt
    dataset_dict['metadata_modified'] = dt

    # Make sure name is unique.
    dataset_dict['name'] = 'copy-of-' + dataset_dict['name']
    dataset_dict['name'] = get_incremental_package_name(dataset_dict['name'])

    dataset_dict.pop('id')

    if 'revision_id' in dataset_dict:
        dataset_dict.pop('revision_id')

    if 'revision_timestamp' in dataset_dict:
        dataset_dict.pop('revision_timestamp')

    # Drop resources.
    if 'resources' in dataset_dict:
        dataset_dict.pop('resources')

    # Drop the relationships for now.
    if 'relationships_as_object' in dataset_dict:
        dataset_dict.pop('relationships_as_object')
    if 'relationships_as_subject' in dataset_dict:
        dataset_dict.pop('relationships_as_subject')

    try:
        for plugin in plugins.PluginImplementations(IClone):
            plugin.clone_modify_dataset(context, dataset_dict)
        get_action('package_create')(context, dataset_dict)
        h.flash_success('Dataset %s is created.' % dataset_dict['title'])
        return h.redirect_to('/dataset')
    except Exception as e:
        log.error(str(e))
        msg = """
        <p>The cloned dataset contains invalid entries:</p>
        <ul>"""
        for key, error in e.error_summary.items():
            msg += "<li>" + key + ": " + error + "</li>"

        msg += """</ul>"""
        h.flash_error(msg, allow_html=True)
        return h.redirect_to('/dataset')


clone_dataset.add_url_rule(u'/clone/<id>', methods=[u'POST'], view_func=clone)
