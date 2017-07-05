import os
import json
import six
import logging


from babbage import BabbageException
from flask import Blueprint, request, current_app
from flask.ext.jsonpify import jsonify

backwardAPI = Blueprint('BackwardAPI', __name__)

TAXONOMIES = json.load(open(os.path.join(os.path.dirname(__file__), 'taxonomies.json')))


log = logging.getLogger()


def configure_backward_api(app, manager):
    """ Configure the current Flask app with an instance of ``CubeManager`` that
    will be used to load and query data. """
    if not hasattr(app, 'extensions'):
        app.extensions = {}  # pragma: nocover
    app.extensions['cube_manager'] = manager
    log.info('SETUP Backward API')
    return backwardAPI


def get_attr_for_dimension_name(model, orig_dim):
    canonized = model.setdefault('_canonized', {})
    if orig_dim in canonized:
        return canonized[orig_dim]
    dim = orig_dim.replace('.', '_')
    attr = None
    if dim in model['dimensions']:
        dim = model['dimensions'][dim]
        attr = dim['attributes'][dim['key_attribute']]
    else:
        for name, dimension in model['dimensions'].items():
            logging.info('%s? %s:%r',
                         dim, name, list(dimension['attributes'].keys()))
            attributes = dimension['attributes']
            name = '_'.join(name.split('_')[1:])
            if name in [dim, dim+'_name']:
                attr = dimension
                attr['datatype'] = attr['attributes'][attr['key_attribute']]['datatype']
            else:
                for attr_name in [dim, dim+'_label', dim+'_name']:
                    if attr_name in attributes:
                        attr = attributes[attr_name]
                        break
            if attr is not None:
                break
        if attr is None:
            for name, dimension in model['dimensions'].items():
                for attr_name, attribute in dimension['attributes'].items():
                    if attr_name.endswith('_'+dim):
                        attr = attribute
                        break
                if attr is not None:
                    break
    assert attr is not None, "Failed to find dimension %s" % dim
    canonized[orig_dim] = attr
    return attr


def canonize_dimension(model, dim, val):
    """
    Convert old-style dimension name to one understandable by babbage.
    Check the datatype of the dimension and cast the given value to the correct type.

    Examples:
        year -> year
        time.year -> year
        functional-classification.func1_label -> func1_code.func1_label

    :param model: the babbage model as Python object
    :param dim: the dimension to be converted (as string)
    :param val: the provided value
    :return: tuple with new dimension name and value
    """
    ret_val = val
    attr = get_attr_for_dimension_name(model, dim)
    ref = attr['ref']
    datatype = attr['datatype']
    if datatype == 'string':
        ret_val = str(ret_val)
    elif datatype == 'integer':
        ret_val = int(ret_val)
    return ref, ret_val


def get_arg_with_default(param, default=None):
    """
    Get from the request's parameters a specific argument.
    If the argument doesn't appear in the request or the value is 'undefined', return the default.
    Use conv callable to attempt a conversion of the resulting value. If the conversion fails, the default is returned.
    :param param: which parameter to fetch
    :param default: default value to use in case of failures
    :param conv: callable to be used to convert the value, may be None in case no conversion is necessary
    :return: fetched value or default
    """
    arg = request.args.get(param,default)
    if arg == 'undefined':
        arg = default
    return arg


@backwardAPI.route('/aggregate')
def backward_compat_aggregate_api():
    """ Implement the old OS aggregate API over Babbage """

    # Fetch general parameters from the request
    orig_dataset = request.args.get('dataset')
    measure_name = get_arg_with_default('measure', 'amount')
    pagesize = request.args.get('pagesize', 10000, int)
    page = request.args.get('page', 1, int)

    dataset = '6018ab87076187018fc29c94a68a3cd2:__os_imported__' + orig_dataset
    log.info('AGGREGATE dataset:%s', dataset)

    # Check if the dataset even exists
    cm = current_app.extensions['cube_manager']
    if cm.has_cube(dataset):
        try:
            cube = cm.get_cube(dataset)
            model = cube.model.to_dict()

            # It there's a dataset, fetch the aggregation params:

            # requested measure
            measure = model['measures'][measure_name]

            # cuts
            cuts = get_arg_with_default('cut')
            if cuts is not None:
                # Cuts for the old API had a simpler syntax
                cuts = cuts.split('|')
                cuts = [c.split(':') for c in cuts if ':' in c]

                # Rename field names from old API to ones that Babbage understands
                canonized_cuts = []
                for k, v in cuts:
                    canonized_cuts.append(canonize_dimension(model, k, v))

                # Rebuild cuts argument
                cuts = '|'.join('%s:%s' % (k,json.dumps(v)) for k,v in canonized_cuts)

            # drilldowns
            orig_drilldowns = get_arg_with_default('drilldown')
            if orig_drilldowns is not None:
                orig_drilldowns = orig_drilldowns.split('|')
                drilldowns = [get_attr_for_dimension_name(model, dd)['ref'] for dd in orig_drilldowns]
                drilldown_translation = dict(zip(drilldowns, orig_drilldowns))
                drilldowns = '|'.join(drilldowns)
            else:
                drilldowns = None

            # result ordering
            order = get_arg_with_default('order')
            if order is not None:
                orders = order.split('|')
                new_orders = []
                for part in orders:
                    parts = part.split(':')
                    if not parts[0].startswith(measure_name+'.sum'):
                        parts[0] = get_attr_for_dimension_name(model, parts[0])['ref']
                    new_orders.append(':'.join(parts))
                order = '|'.join(new_orders)
            else:
                measure_name+'.sum:desc'

            # Call babbage and watch out for errors
            try:
                aggregate = cube.aggregate(cuts=cuts, drilldowns=drilldowns,page_size=pagesize,page=page,order=order)
            except BabbageException as e:
                return jsonify({'errors': [str(e)]})

            # Process the results to build a backward-compatible response

            logging.info('Original AGGREGATE result:\n%s',
                         json.dumps(aggregate, indent=2))

            # General parameters
            count = aggregate['summary']['_count']
            pagesize = aggregate['page_size']
            numcells = len(aggregate['cells'])
            total_cell_count = aggregate['total_cell_count']
            pages = 0
            if numcells>0:
                pages = (total_cell_count-1)//pagesize+1
            ret = dict([
                ('summary', dict([
                    ('amount', aggregate['summary'][measure_name+'.sum']),
                    ('currency', { measure_name: measure['currency']} if 'currency' in measure else {}),
                    ('num_drilldowns', total_cell_count),
                    ('num_entries', count),
                    ('page', aggregate['page']),
                    ('pages', pages),
                    ('pagesize', pagesize),
                    ])
                 ),
            ])

            # Now process the cell data
            canonized = model.get('_canonized', {})
            ret['drilldown'] = []
            for cell in aggregate['cells']:
                drilldown = {}
                for k, v in cell.items():
                    if k == measure_name+'.sum':
                        drilldown[measure_name] = v
                    elif k == '_count':
                        drilldown['num_entries'] = v
                    elif '.' in k:
                        if type(v) is bool:
                            v = json.dumps(v)
                        elif type(v) in six.integer_types:
                            v = str(v)
                        dd_dim = k.split('.')[0]
                        dd_dim = drilldown_translation.get(dd_dim, dd_dim)
                        dim_parts = dd_dim.split('.')
                        dd_dim = dim_parts[0]
                        logging.error('dd_dim=%s, to_dim=%s, attr=%r',
                                      dd_dim, drilldown_translation.get(dd_dim), drilldown_translation)
                        if dd_dim not in drilldown:
                            drilldown[dd_dim] = {}
                            taxonomy_rules = TAXONOMIES.get(dataset,{})
                            taxonomy = taxonomy_rules.get(dd_dim, dd_dim)
                            drilldown[dd_dim]['taxonomy'] = taxonomy

                        attr = '.'.join(dim_parts[1:])
                        # if attr.startswith(dd_dim):
                        #     attr = attr[len(dd_dim)+1:]
                        drilldown[dd_dim][attr] = v
                        if attr == 'name':
                            html_url = 'https://openspending.org/%s/%s/%s' % (dataset, dd_dim,v)
                            drilldown[dd_dim]['html_url'] = html_url
                            drilldown[dd_dim]['id'] = hash(html_url) % 1000 + 1000

                ret['drilldown'].append(drilldown)

            return jsonify(ret)

        except Exception as e:
            logging.exception('Error in handling')
            return jsonify({'errors':[str(e)]})

    return jsonify({'errors':['no dataset with name "%s"' % orig_dataset]})
