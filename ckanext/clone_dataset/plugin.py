import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic.auth.create as auth_create

from ckanext.clone_dataset import blueprint, overrides


class CloneDatasetPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurable, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'clone_dataset')

    # IBlueprint
    def get_blueprint(self):
        return blueprint.clone_dataset

    # IConfigurable
    def configure(self, config):
        auth_create._check_group_auth = overrides._check_group_auth
