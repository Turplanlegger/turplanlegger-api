from flask import jsonify, request

from turplanlegger.exceptions import ApiError
from turplanlegger.models.note import Note

from . import api


@api.route('/note/<note_id>', methods=['GET'])
def get_note(note_id):

    note = Note.find_note(note_id)

    if note:
        return jsonify(status='ok', count=1, note=note.serialize)
    else:
        raise ApiError('note not found', 404)


@api.route('/note/<note_id>', methods=['DELETE'])
def delete_note(note_id):

    note = Note.find_note(note_id)

    if not note:
        raise ApiError('note not found', 404)

    try:
        note.delete()
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')


@api.route('/note', methods=['POST'])
def add_note():
    try:
        note = Note.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiError(str(e), 400)

    try:
        note = note.create()
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(note.serialize), 201


@api.route('/note/<note_id>/owner', methods=['PATCH'])
def change_note_owner(note_id):

    note = Note.find_note(note_id)

    if not note:
        raise ApiError('note not found', 404)

    owner = request.json.get('owner', None)

    if not owner:
        raise ApiError('must supply owner as int', 400)

    try:
        note.change_owner(owner)
    except ValueError as e:
        raise ApiError(str(e), 400)
    except Exception as e:
        raise ApiError(str(e), 500)

    return jsonify(status='ok')

@api.route('/note/<note_id>/rename', methods=['PATCH'])
def rename_note(note_id):

    note = Note.find_note(note_id)

    if not note:
        raise ApiError('note not found', 404)

    note.name = request.json.get('name', '')

    if note.rename():
        return jsonify(status='ok')
    else:
        raise ApiError('failed to rename note')
