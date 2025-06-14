from uuid import UUID

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

    if (
        note
        and Permission.verify(note.owner, note.permissions, g.user.id, AccessLevel.READ) is PermissionResult.ALLOWED
    ):
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
    note_existing = Note.find_note(note_id)

    if not note_existing:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    perms = Permission.verify(note_existing.owner, note_existing.permissions, g.user.id, AccessLevel.MODIFY)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)
    if perms is PermissionResult.INSUFFICIENT_PERMISSIONS:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to modify the note', 403)

    try:
        note_update = Note.parse(request.json)
    except (ValueError, TypeError) as e:
        raise ApiProblem('Failed to parse note update', str(e), 400)

    updated = False

    for attribute in ('content', 'name'):
        if note_update.__getattribute__(attribute) != note_existing.__getattribute__(attribute):
            note_existing.__setattr__(attribute, note_update.__getattribute__(attribute))
            updated = True

    if updated is True:
        try:
            note = note_existing.update()
        except Exception as e:
            raise ApiProblem('Failed to update note', str(e), 500)
    else:
        note = note_existing

    return jsonify(status='ok', count=1, note=note.serialize)


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


@api.route('/notes/<note_id>/permissions', methods=['PATCH'])
@auth
def add_permissions(note_id):
    note = Note.find_note(note_id)
    if not note:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    perms = Permission.verify(note.owner, note.permissions, g.user.id, AccessLevel.READ)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    if note.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to add note permissions', 403)

    permissions_input = request.json.get('permissions', [])

    if not isinstance(permissions_input, list) or not permissions_input:
        raise ApiProblem('Bad Request', 'You must supply a non‐empty "permissions" array', 400)

    new_permissions = []
    for perm in permissions_input:
        if perm.get('object_id', None) is None:
            perm['object_id'] = note.id
            new_permissions.append(perm)
            continue
        if perm.get('object_id', None) != note.id:
            continue

    try:
        permissions = tuple(Permission.parse(permission) for permission in new_permissions)
    except ValueError:
        raise ApiProblem('Failed to add new permissions', 'No new permissions were parsed', 400)

    for perm in permissions:
        if perm in note.permissions:
            raise ApiProblem('Failed to add permissions', 'The permission already exists', 409)

    try:
        new_permissions = note.add_permissions(permissions)
    except ValueError as e:
        raise ApiProblem('Failed to add new permissions', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to add new permissions', str(e), 500)

    if len(new_permissions) > 0:
        return jsonify(status='ok', permissions=tuple(perm.serialize for perm in new_permissions))
    else:
        raise ApiProblem('Failed to add new permissions', 'No new permissions were parsed', 400)


@api.route('/notes/<note_id>/permissions/<user_id>', methods=['DELETE'])
@auth
def delete_permissions(note_id, user_id):
    note = Note.find_note(note_id)
    if not note:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    perms = Permission.verify(note.owner, note.permissions, g.user.id, AccessLevel.READ)
    if perms is PermissionResult.NOT_FOUND:
        raise ApiProblem('Note not found', 'The requested note was not found', 404)

    user_id = UUID(user_id)

    if g.user.id != user_id and note.owner != g.user.id:
        raise ApiProblem('Insufficient permissions', 'Not sufficient permissions to remove note permissions', 403)

    permission = next((perm for perm in note.permissions if perm.subject_id == user_id), None)

    if permission is None:
        raise ApiProblem('Failed to delete permissions', 'User not found in permissions', 400)

    try:
        note.delete_permission(permission)
    except ValueError as e:
        raise ApiProblem('Failed to delete permissions', str(e), 400)
    except Exception as e:
        raise ApiProblem('Failed to delete permissions', str(e), 500)

    return ('', 204)
