from flask import jsonify, request

from turplanlegger.auth.decorators import auth
from turplanlegger.exceptions import ApiProblem
from turplanlegger.models.note import Note

from . import api


@api.route('/note/<note_id>', methods=['GET'])
@auth
def get_note(note_id):

    note = Note.find_note(note_id)

    if note:
        return jsonify(status='ok', count=1, note=note.serialize)
    else:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)


@api.route('/note/<note_id>', methods=['DELETE'])
@auth
def delete_note(note_id):

    note = Note.find_note(note_id)

    if not note:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    try:
        note.delete()
    except Exception as e:
        raise ApiProblem('Failed to delete note', str(e), 500)

    return jsonify(status='ok')


@api.route('/note', methods=['POST'])
@auth
def add_note():
    try:
        note = Note.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiProblem('Failed to parse note', str(e), 400)

    try:
        note = note.create()
    except Exception as e:
        raise ApiProblem('Failed to create note', str(e), 500)

    return jsonify(note.serialize), 201


@api.route('/note/<note_id>/owner', methods=['PATCH'])
@auth
def change_note_owner(note_id):

    note = Note.find_note(note_id)

    if not note:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    owner = request.json.get('owner', None)

    if not owner:
        raise ApiProblem('Owner is not int', 'Owner must be passed as an int', 400)

    try:
        note.change_owner(owner)
    except ValueError as e:
        raise ApiProblem('Failed to change owner of note', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to change owner of note', str(e), 500)

    return jsonify(status='ok')


@api.route('/note/<note_id>/rename', methods=['PATCH'])
@auth
def rename_note(note_id):

    note = Note.find_note(note_id)

    if not note:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    note.name = request.json.get('name', '')

    if note.rename():
        return jsonify(status='ok')
    else:
        raise ApiProblem('Failed to rename note', 'Unknown error', 500)


@api.route('/note/<note_id>/update', methods=['PATCH'])
@auth
def update_note(note_id):

    note = Note.find_note(note_id)

    if not note:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    note.content = request.json.get('content', '')

    if note.update():
        return jsonify(status='ok')
    else:
        raise ApiProblem('Failed to update note', 'Unknown error', 500)
