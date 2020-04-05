from flask import (
    Blueprint, g, redirect, request, url_for, jsonify
)

from werkzeug.exceptions import abort

from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todolist', __name__)

@bp.route('/')
def index():
    db = get_db()
    todolist = db.execute(
        'SELECT t.id, title, body, created, author_id, username'
        ' FROM todo t JOIN user u ON t.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    data = []
    for todo in todolist:
        data.append(list(todo))

    return jsonify(data)

@bp.route('/create', methods =('POST',))
@login_required
def create():
    title = request.form['title']
    body = request.form['body']
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        return error
    else:
        db = get_db()
        db.execute(
            'INSERT INTO todo (title, body, author_id)'
            ' VALUES (?, ?, ?)',
            (title, body, g.user['id'])
        )

        db.commit()

        return redirect(url_for('todolist.index'))

@bp.route('/<int:id>/update', methods=('POST',))
@login_required
def update(id):
    todo = get_todo(id)
    title = request.form['title']
    body = request.form['body']
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        return error
    else:
        db = get_db()
        db.execute(
            'UPDATE todo SET title = ?, body = ?'
            ' WHERE id = ?',
            (title, body, id)
        )
        db.commit()

    return redirect(url_for('todolist.index'))

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_todo(id)
    db = get_db()
    db.execute('DELETE FROM todo WHERE id=?', (id,))
    db.commit()
    return redirect(url_for('todolist.index'))

def get_todo(id, check_author=True):
    todo = get_db().execute(
        'SELECT t.id, title, body, created, author_id, username'
        ' FROM todo t JOIN user u ON t.author_id = u.id'
        ' WHERE t.id = ?', (id,)
    ).fetchone()

    if todo is None:
        abort(404, "Todo id {0} doesn't exist.".format(id))

    if check_author and todo['author_id'] != g.user['id']:
        abort(403)

    return todo