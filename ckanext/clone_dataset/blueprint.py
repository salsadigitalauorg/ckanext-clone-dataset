import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import logging
import datetime

from pprint import pformat
from flask import Blueprint
from ckan.plugins.toolkit import get_action
from ckanext.clone_dataset.helpers import get_incremental_package_name

clean_dict = logic.clean_dict
h = toolkit.h
log = logging.getLogger(__name__)
parse_params = logic.parse_params
request = toolkit.request
tuplize_dict = logic.tuplize_dict
NotAuthorized = toolkit.NotAuthorized

clone_dataset = Blueprint('clone_dataset', __name__, url_prefix=u'/ckan-admin')


def clone(id):
    # Get current dataset.
    try:
        # Need to set the user info in the context for check_access
        context = {'user': toolkit.g.user, 'userobj': toolkit.g.userobj}
        # Check the user has permission to clone the dataset
        toolkit.check_access('package_update', context, {'id': id})

        dataset_dict = get_action('package_show')({}, {'id': id})
    except NotAuthorized as e:
        log.error(str(e))
        h.flash_error(str(e))
        return h.redirect_to('/dataset')
    except Exception as e:
        log.error('Error loading dataset. id:%s' % id)
        h.flash_error('Error loading dataset. {0}'.format(str(e)))
        return h.redirect_to('/dataset')

    # Update necessary fields.
    dt = datetime.datetime.utcnow().isoformat()
    dataset_dict['title'] = 'COPY of - ' + dataset_dict['title']
    dataset_dict['metadata_created'] = dt
    dataset_dict['metadata_modified'] = dt

    # Make sure name is unique.
    dataset_dict['name'] = 'copy-of-' + dataset_dict['name']
    dataset_dict['name'] = get_incremental_package_name(dataset_dict['name'])

    dataset_dict.pop('id')

    if 'identifiers' in dataset_dict:
        dataset_dict.pop('identifiers')

    if 'revision_id' in dataset_dict:
        dataset_dict.pop('revision_id')

    if 'revision_timestamp' in dataset_dict:
        dataset_dict.pop('revision_timestamp')

    if 'metadata_review_date' in dataset_dict:
        dataset_dict.pop('metadata_review_date')

    # Drop resources.
    if 'resources' in dataset_dict:
        dataset_dict.pop('resources')

    # Drop the relationships for now.
    if 'relationships_as_object' in dataset_dict:
        dataset_dict.pop('relationships_as_object')
    if 'relationships_as_subject' in dataset_dict:
        dataset_dict.pop('relationships_as_subject')
    # Also drop any specific fields that may contain references that trigger relationship creation
    if 'series_or_collection' in dataset_dict:
        dataset_dict.pop('series_or_collection')
    if 'related_resources' in dataset_dict:
        dataset_dict.pop('related_resources')

    try:
        get_action('package_create')({}, dataset_dict)
        h.flash_success('Dataset %s is created.' % dataset_dict['title'])
        return h.redirect_to('/dataset')
    except Exception as e:
        log.error(str(e))
        h.flash_error('Error cloning dataset.')
        return h.redirect_to('/dataset')


clone_dataset.add_url_rule(u'/clone/<id>', methods=[u'POST'], view_func=clone)
