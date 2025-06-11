from IPython import embed
from flask import g, jsonify, request

from turplanlegger.auth.decorators import auth
from turplanlegger.exceptions import ApiProblem
from turplanlegger.models.access_level import AccessLevel
from turplanlegger.models.note import Note
from turplanlegger.models.permission import Permission, PermissionResult

from . import api


@api.route('/notes/<note_id>', methods=['GET'])
@auth
def get_note(note_id):
    note = Note.find_note(note_id)

    if note and Permission.verify(note.owner, note.permissions, g.user.id, AccessLevel.READ) is PermissionResult.ALLOWED:
        return jsonify(status='ok', count=1, note=note.serialize)
    else:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)


@api.route('/notes/<note_id>', methods=['DELETE'])
@auth
def delete_note(note_id):
    note = Note.find_note(note_id)

    if note is None:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    perms = Permission.verify(note.owner, note.permissions, g.user.id, AccessLevel.DELETE)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)
    if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to delete the note', 403)

    try:
        note.delete()
    except Exception as e:
        raise ApiProblem('Failed to delete note', str(e), 500)

    return jsonify(status='ok')


@api.route('/notes', methods=['POST'])
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


@api.route('/notes/<note_id>', methods=['PUT'])
@auth
def update_note(note_id):
    note = Note.find_note(note_id)

    if not note:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    perms = Permission.verify(note.owner, note.permissions, g.user.id, AccessLevel.MODIFY)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)
    if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the note', 403)

    name = request.json.get('name', None)
    content = request.json.get('content', None)

    if content is None:
        raise ApiProblem('Failed to update note', 'Field content can not be empty', 409)

    if name == note.name and content == note.content:
        raise ApiProblem('Failed to update note', 'No new updates were provided', 409)

    note.name = name
    note.content = content

    if note.update():
        return jsonify(status='ok', count=1, note=note.serialize)
    else:
        raise ApiProblem('Failed to update note', 'Unknown error', 500)


@api.route('/notes/<note_id>/owner', methods=['PATCH'])
@auth
def change_note_owner(note_id):
    note = Note.find_note(note_id)

    if not note:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    perms = Permission.verify(note.owner, note.permissions, g.user.id, AccessLevel.READ)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)
    
    if note.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to change owner the note', 403)

    owner = request.json.get('owner', None)

    if not owner:
        raise ApiProblem('Owner is not int', 'Owner must be passed as an str', 400)

    try:
        note.change_owner(owner)
    except ValueError as e:
        raise ApiProblem('Failed to change owner of note', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to change owner of note', str(e), 500)

    return jsonify(status='ok')


@api.route('/notes/<note_id>/rename', methods=['PATCH'])
def rename_note(note_id):
    raise ApiProblem('Endpoint has been deprecated', 'Use PUT /notes/<note_id> instead', 410)


@api.route('/notes/<note_id>/content', methods=['PATCH'])
def update_note_content(note_id):
    raise ApiProblem('Endpoint has been deprecated', 'Use PUT /notes/<note_id> instead', 410)


@api.route('/notes/mine', methods=['GET'])
@auth
def get_my_notes():
    notes = Note.find_note_by_owner(g.user.id)

    if notes:
        return jsonify(status='ok', count=len(notes), note=[note.serialize for note in notes])
    else:
        raise ApiProblem('Note not found', 'No notes were found for the requested user', 404)
