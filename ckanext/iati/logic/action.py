import json
import csv
import tempfile
from urlparse import urljoin

from pylons import config

from ckan import logic

import ckan.plugins as p
from ckan.logic.action.get import package_show_rest as package_show_rest_core
from ckan.logic.action.create import package_create as package_create_core
from ckan.logic.action.update import package_update as package_update_core


def package_create(context, data_dict):
    '''
        The only thing we do here is remove some extras that are always
        inherited from the dataset publisher, to avoid duplicating them
    '''
    _remove_extras_from_data_dict(data_dict)

    return package_create_core(context, data_dict)


def package_update(context, data_dict):
    '''
        The only thing we do here is remove some extras that are always
        inherited from the dataset publisher, to avoid duplicating them
    '''
    _remove_extras_from_data_dict(data_dict)

    return package_update_core(context, data_dict)


def _remove_extras_from_data_dict(data_dict):
    # Remove these extras, as they are always inherited from the publishers
    # and we don't want to store them
    extras_to_remove = ('publishertype',
                        'publisher_organization_type',
                        'publisher_country',
                        'publisher_iati_id',
                       )
    data_dict['extras'] = [e for e in data_dict.get('extras', []) if e['key'] not in extras_to_remove]


@p.toolkit.side_effect_free
def package_show_rest(context, data_dict):
    '''
        Add some extras to the dataset from its publisher.

        The ideal place to do this should be the after_show hook on the
        iati_datasets plugin but package_show_rest does not call it in core.
    '''
    package_dict = package_show_rest_core(context, data_dict)

    group = context['package'].groups[0] if len(context['package'].groups) else None
    if group:
        new_extras = {
            'publishertype':group.extras.get('type', ''),
            'publisher_organization_type':group.extras.get('publisher_organization_type', ''),
            'publisher_country':group.extras.get('publisher_country', ''),
            'publisher_iati_id':group.extras.get('publisher_iati_id', ''),
        }

        package_dict['extras'].update(new_extras)

    return package_dict


def issues_report_csv(context, data_dict):

    logic.check_access('issues_report_csv', context, data_dict)

    publisher_name = data_dict.get('publisher', None)

    issues = {}

    # Get packages with issues
    if publisher_name:
        result = packages_with_issues_for_a_publisher(context, publisher_name)
        if result['count'] > 0:
            issues[publisher_name] = result['results']

    else:
        # Get all the publishers whose datasets have issues
        data_dict = {
            'q': 'issue_type:[\'\' TO *]',
            'facet.field': 'groups',
            'rows': 0,
        }
        result = logic.get_action('package_search')(context, data_dict)
        if result['count'] > 0:
            publishers = result['facets']['groups']
            for publisher_name, count in publishers.iteritems():
                result = packages_with_issues_for_a_publisher(context, publisher_name)
                issues[publisher_name] = result['results']


    fd, tmp_file_path = tempfile.mkstemp(suffix='.csv')

    def get_extra(pkg_dict, key, default=None):
        for extra in pkg_dict['extras']:
            if extra['key'] == key:
                if extra['value'][:1] == '"':
                    extra['value'] = json.loads(extra['value'])
                return extra['value']

        return default


    site_url = config.get('ckan.site_url', 'http://iatiregistry.org')

    with open(tmp_file_path, 'w') as f:
        field_names = ['publisher', 'dataset', 'url', 'file_url', 'issue_type', 'issue_date', 'issue_message']
        writer = csv.DictWriter(f, fieldnames=field_names, quoting=csv.QUOTE_ALL)
        writer.writerow(dict( (n,n) for n in field_names ))
        for publisher, datasets in issues.iteritems():
            for dataset in datasets:
                url = urljoin(site_url, '/dataset/' + dataset['name'])
                if len(dataset['resources']):
                    file_url = dataset['resources'][0]['url']
                else:
                    file_url = ''

                writer.writerow({
                    'publisher': publisher,
                    'dataset': dataset['name'],
                    'url': url,
                    'file_url': file_url,
                    'issue_type': get_extra(dataset, 'issue_type', ''),
                    'issue_date': get_extra(dataset, 'issue_date', ''),
                    'issue_message': get_extra(dataset, 'issue_message', ''),
                })

        return {
            'file': tmp_file_path,
        }


def packages_with_issues_for_a_publisher(context, publisher_name):
        data_dict = {
            'q': 'issue_type:[\'\' TO *]',
            'fq': 'groups:{0}'.format(publisher_name),
            'rows': 1000,
        }

        return logic.get_action('package_search')(context, data_dict)
