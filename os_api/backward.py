import json

from babbage import BabbageException, QueryException
from flask import Blueprint, request, current_app, jsonify

from babbage.query.cuts import Cuts


class SafeCuts(Cuts):

    def cut(self, ast):
        self.results.append((ast[0], ast[1], ast[2]))

backwardAPI = Blueprint('BackwardAPI', __name__)


def configure_backward_api(app, manager):
    """ Configure the current Flask app with an instance of ``CubeManager`` that
    will be used to load and query data. """
    if not hasattr(app, 'extensions'):
        app.extensions = {}  # pragma: nocover
    app.extensions['cube_manager'] = manager
    return backwardAPI


def canonize_dimension(model, dim, val):
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
                if parts[1] == name:
                    ret_dim = name
                    break
                elif parts[1] in dimension['attributes'] and parts[0] == dimension.get('group'):
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
        ret_val = unicode(ret_val)
    elif datatype == 'integer':
        ret_val = int(ret_val)
    if ret_attr is None:
        return ret_dim, ret_val
    else:
        return ret_dim+'.'+ret_attr, ret_val


def get_arg_with_default(param, default=None, conv=None):
    arg = request.args.get(param,default)
    if arg=='undefined':
        arg = default
    if conv is not None:
        try:
            arg = conv(arg)
        except ValueError:
            arg = default
    return arg

@backwardAPI.route('/aggregate')
def backward_compat_aggregate_api():
    dataset = request.args.get('dataset')
    measure_name = get_arg_with_default('measure', 'amount')
    pagesize = request.args.get('pagesize', 10000, int)
    page = request.args.get('page', 1, int)

    cm = current_app.extensions['cube_manager']
    if cm.has_cube(dataset):
        model = cm.get_cube_model(dataset)
        measure = model['measures'][measure_name]
        cube = cm.get_cube(dataset)
        cuts = get_arg_with_default('cut')
        if cuts is not None:
            try:
                cuts = SafeCuts(cube).parse(cuts)
            except BabbageException as e:
                return jsonify({'errors':str(e)})

            canonized_cuts = []
            for k,_,v in cuts:
                canonized_cuts.append(canonize_dimension(model, k, v))
            cuts = '|'.join( '%s:%s' % (k,json.dumps(v)) for k,v in canonized_cuts )

        drilldowns = get_arg_with_default('drilldown')
        order = get_arg_with_default('order', measure_name+'.sum:desc')

        print cuts, drilldowns
        try:
            aggregate = cube.aggregate(cuts=cuts, drilldowns=drilldowns,page_size=pagesize,page=page,order=order)
        except BabbageException as e:
            return jsonify({'errors':str(e)})


        # aggregate['cells'].sort(key=lambda x:x[measure_name+'.sum'], reverse=True)

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
                    elif type(v) in (int,long):
                        v = str(v)
                    parts = k.split('.')
                    drilldown.setdefault(parts[0],{})['.'.join(parts[1:])] = v
                    if parts[1] == 'name':
                        drilldown[parts[0]]['html_url'] =\
                         'https://openspending.org/%s/%s/%s' % (dataset,parts[0],v)

            ret['drilldown'].append(drilldown)

        return jsonify(ret)
    return jsonify({'errors':'no such dataset'})
