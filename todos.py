"""
ToDos REST API with HATEOAS (HAL-style)

Based on:
"Programming Foundations: APIs and Web Services"
Kesha Williams (LinkedIn Learning, 2025)
"""

from flask import Flask, jsonify, request, url_for

app = Flask(__name__)

# Sample in-memory to-do list
todos = [
    {'id': 1, 'task': 'Learn Flask', 'done': False},
    {'id': 2, 'task': 'Build a REST API', 'done': False},
    {'id': 3, 'task': 'Test the API', 'done': False},
    {'id': 4, 'task': 'Watch another course from Kesha', 'done': False},
    {'id': 5, 'task': 'Learn Laravel', 'done': False},
    {'id': 6, 'task': 'Build a GraphQL API', 'done': False},
    {'id': 7, 'task': 'Learn Java Spring', 'done': False},
    {'id': 8, 'task': 'Build a gRPC API', 'done': False},
    {'id': 9, 'task': 'Learn .NET', 'done': False},
    {'id': 10, 'task': 'Build a SOAP API', 'done': False},
    {'id': 11, 'task': 'Learn Django', 'done': False},
    {'id': 12, 'task': 'Document an API', 'done': False},
    {'id': 13, 'task': 'Learn Node.js', 'done': False},
    {'id': 14, 'task': 'Secure an API', 'done': False},
    {'id': 15, 'task': 'Learn Next.js', 'done': False},
    {'id': 16, 'task': 'Build a WebSockets connection', 'done': False},
]


def find_todo(todo_id):
    return next((todo for todo in todos if todo['id'] == todo_id), None)


# -----------------------------
# HATEOAS helpers
# -----------------------------
def add_todo_links(todo):
    """Return a HAL-style representation of one todo."""
    return {
        **todo,
        '_links': {
            'self': {'href': url_for('get_todo', todo_id=todo['id'], _external=True)},
            'update': {'href': url_for('update_todo', todo_id=todo['id'], _external=True)},
            'delete': {'href': url_for('delete_todo', todo_id=todo['id'], _external=True)},
            'collection': {'href': url_for('get_todos', _external=True)}
        }
    }


def add_collection_links(items, offset, size, total_items):
    """Return a HAL-style list with navigation links and pagination metadata."""
    # Base self URL with current pagination
    self_url = url_for('get_todos', offset=offset, size=size, _external=True)

    links = {
        'self': {'href': self_url},
        'create': {'href': url_for('create_todo', _external=True)},
    }

    # Previous page
    if offset > 0:
        prev_offset = max(offset - size, 0)
        links['prev'] = {
            'href': url_for('get_todos', offset=prev_offset, size=size, _external=True)
        }

    # Next page
    if offset + size < total_items:
        next_offset = offset + size
        links['next'] = {
            'href': url_for('get_todos', offset=next_offset, size=size, _external=True)
        }

    return {
        '_links': links,
        '_embedded': {
            'todos': [add_todo_links(t) for t in items]
        },
        'page': {
            'offset': offset,
            'size': size,
            'total_items': total_items
        }
    }


# -----------------------------
# Routes
# -----------------------------

@app.route('/todos', methods=['GET'])
def get_todos():
    # Pagination params
    offset = request.args.get('offset', default=0, type=int)
    size = request.args.get('size', default=5, type=int)

    if offset < 0 or size <= 0:
        return jsonify({
            'error': 'Invalid pagination parameters. Offset must be >= 0 and size must be > 0.'
        }), 400

    total_items = len(todos)
    paged_items = todos[offset:offset + size]

    return jsonify(add_collection_links(paged_items, offset, size, total_items)), 200


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = find_todo(todo_id)
    if not todo:
        return jsonify({'error': 'To-do item not found'}), 404
    return jsonify(add_todo_links(todo)), 200


@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.json
    if not data or 'task' not in data:
        return jsonify({'error': 'Task description is required'}), 400

    new_todo = {
        'id': max(todo['id'] for todo in todos) + 1 if todos else 1,
        'task': data['task'],
        'done': data.get('done', False)
    }
    todos.append(new_todo)

    return jsonify({
        'message': 'To-do item created',
        'todo': add_todo_links(new_todo)
    }), 201


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = find_todo(todo_id)
    if not todo:
        return jsonify({'error': 'To-do item not found'}), 404

    data = request.json or {}
    todo['task'] = data.get('task', todo['task'])
    todo['done'] = data.get('done', todo['done'])

    return jsonify({
        'message': 'To-do item updated',
        'todo': add_todo_links(todo)
    }), 200


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todos = [todo for todo in todos if todo['id'] != todo_id]

    return jsonify({
        'message': f'To-do item with ID {todo_id} deleted',
        '_links': {
            'collection': {'href': url_for('get_todos', _external=True)}
        }
    }), 200


# -----------------------------
# Header versioning
# -----------------------------
@app.after_request
def add_custom_headers(response):
    response.headers['Content-Type'] = 'application/json'
    response.headers['X-API-Version'] = '2'

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)