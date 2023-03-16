
from ckan.plugins.interfaces import Interface


class IClone(Interface):
    u'''
    This interface allows plugins to hook into the Clone workflow
    '''
    def clone_modify_dataset(self, context, dataset_dict):
        u'''
        Allow extensions to modify the dataset dictionary before the new cloned dataset is created

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param dataset_dict: Dataset dictionary from source dataset via package_show action that can be modified before it is created via the package_create action.
        :type resource: dictionary
        '''
        pass
