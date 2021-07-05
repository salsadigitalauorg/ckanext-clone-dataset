import ckan.plugins.toolkit as toolkit
import ckan.authz as authz


def _check_group_auth(context, data_dict):
    ''' Copied from ckan.logic.auth.create._check_group_auth
        Has this user got update permission for all of the given groups?
        If there is a package in the context then ignore that package's groups.
        (owner_org is checked elsewhere.)
        :returns: False if not allowed to update one (or more) of the given groups.
                True otherwise. i.e. True is the default. A blank data_dict
                mentions no groups, so it returns True.
    '''
    # FIXME This code is shared amoung other logic.auth files and should be
    # somewhere better
    if not data_dict:
        return True

    model = context['model']
    user = context['user']
    pkg = context.get("package")

    api_version = context.get('api_version') or '1'

    group_blobs = data_dict.get('groups', [])
    groups = set()
    for group_blob in group_blobs:
        # group_blob might be a dict or a group_ref
        if isinstance(group_blob, dict):
            # use group id by default, but we can accept name as well
            id = group_blob.get('id') or group_blob.get('name')
            if not id:
                continue
        else:
            id = group_blob
        grp = model.Group.get(id)
        if grp is None:
            raise toolkit.ObjectNotFound(toolkit._('Group was not found.'))
        groups.add(grp)

    if pkg:
        pkg_groups = pkg.get_groups()

        groups = groups - set(pkg_groups)

    for group in groups:
        # QDES Modification.
        # Only check user permission if group is not an organisation and is not coming from clone_dataset
        # When we a cloning a dataset we need to ignore group (categories)
        # Any user can add their organisation datasets to a category
        if group.is_organization or not toolkit.get_endpoint() == ('clone_dataset', 'clone'):
            if not authz.has_user_permission_for_group_or_org(group.id, user, 'manage_group'):
                return False

    return True
