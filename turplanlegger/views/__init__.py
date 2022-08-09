from flask import Blueprint, current_app, jsonify, request

from turplanlegger.exceptions import ApiProblem
from turplanlegger.utils.response import absolute_url

api = Blueprint('api', __name__)  # noqa isort:skip

from . import item_lists, notes, routes, users, trips  # noqa isort:skip


@api.before_request
def before_request():
    if ((request.method in ['POST', 'PUT'] or (request.method == 'PATCH' and request.data))
            and not request.is_json):
        raise ApiProblem(
            'Request has wrong Content-Type',
            'PATCH, POST and PUT requests must set \'Content-type\' to \'application/json\'',
            415
        )


@api.route('/', methods=['GET'])
def index():
    links = []

    for rule in current_app.url_map.iter_rules():
        links.append({
            'rel': rule.endpoint,
            'href': absolute_url(rule.rule),
            'method': ','.join([m for m in rule.methods
                               if m not in ['HEAD', 'OPTIONS']])})

    return jsonify(status='ok', uri=absolute_url(),
                   data={'description': 'Turplanlegger API'},
                   links=sorted(links, key=lambda
                   k: k['href']))


@api.route('/test', methods=['GET'])
def test():
    return jsonify(status='ok')
