import os
import json
import six

from babbage import BabbageException
from flask import Blueprint, request, current_app
from flask.ext.jsonpify import jsonify

backwardAPI = Blueprint('BackwardAPI', __name__)

TAXONOMIES = json.load(open(os.path.join(os.path.dirname(__file__), 'taxonomies.json')))

def configure_backward_api(app, manager):
    """ Configure the current Flask app with an instance of ``CubeManager`` that
    will be used to load and query data. """
    if not hasattr(app, 'extensions'):
        app.extensions = {}  # pragma: nocover
    app.extensions['cube_manager'] = manager
    return backwardAPI


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
    ret_dim = dim
    ret_val = val
    ret_attr = None
    if dim in model['dimensions']:
        ret_dim = dim
    else:
        for name, dimension in model['dimensions'].items():
            if dim in dimension['attributes']:
                ret_dim = name
                break
            elif '.' in dim:
                parts = dim.split('.')
                if parts[1] in dimension['attributes'] and parts[0] == dimension.get('hierarchy'):
                    ret_dim = name
                    ret_attr = parts[1]
                    break
    dimension = model['dimensions'][ret_dim]
    key_attr = dimension['key_attribute']
    if ret_attr is None:
        attribute = dimension['attributes'][key_attr]
    else:
        attribute = dimension['attributes'][ret_attr]
        if ret_attr == key_attr:
            ret_attr = None
    datatype = attribute['datatype']
    if datatype == 'string':
        ret_val = str(ret_val)
    elif datatype == 'integer':
        ret_val = int(ret_val)
    if ret_attr is None:
        return ret_dim, ret_val
    else:
        return ret_dim+'.'+ret_attr, ret_val


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
    dataset = request.args.get('dataset')
    measure_name = get_arg_with_default('measure', 'amount')
    pagesize = request.args.get('pagesize', 10000, int)
    page = request.args.get('page', 1, int)

    # Check if the dataset even exists
    cm = current_app.extensions['cube_manager']
    if cm.has_cube(dataset):
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
        drilldowns = get_arg_with_default('drilldown')

        # result ordering
        order = get_arg_with_default('order', measure_name+'.sum:desc')

        # Call babbage and watch out for errors
        try:
            aggregate = cube.aggregate(cuts=cuts, drilldowns=drilldowns,page_size=pagesize,page=page,order=order)
        except BabbageException as e:
            return jsonify({'errors': [str(e)]})

        # Process the results to build a backward-compatible response

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
        ret['drilldown']=[]
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
                    parts = k.split('.')
                    if parts[0] not in drilldown:
                        drilldown[parts[0]] = {}
                        taxonomy_rules = TAXONOMIES.get(dataset,{})
                        taxonomy = taxonomy_rules.get(parts[0],parts[0])
                        drilldown[parts[0]]['taxonomy'] = taxonomy

                    drilldown[parts[0]]['.'.join(parts[1:])] = v
                    if parts[1] == 'name':
                        html_url = 'https://openspending.org/%s/%s/%s' % (dataset,parts[0],v)
                        drilldown[parts[0]]['html_url'] = html_url
                        drilldown[parts[0]]['id'] = hash(html_url) % 1000 + 1000



            ret['drilldown'].append(drilldown)

        return jsonify(ret)
    return jsonify({'errors':['no dataset with name "%s"' % dataset]})
