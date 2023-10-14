from flask import Flask, request, render_template
import todos_db as db
import json

db.init()
app = Flask(__name__)


def tmpl(attr):
    return attr.replace('--', '/').replace('-', '_') + '.html.j2'


def tmpl_name(arg):
    if isinstance(arg, str):
        template_name = arg
    else:
        template_name = arg._TemplateReference__context.name

    suffix_length = len(".html.j2")
    return template_name[:-suffix_length].replace('/', '--').replace('_', '-')


app.jinja_env.globals.update(
    tmpl=tmpl,
    tmpl_name=tmpl_name
)


@app.route("/")
def index():
    todos = db.list_todos()
    return render_template('index.html.j2', todos=todos)


@app.route("/todolist/item/<int:id>")
def show_todo(id):
    todo = db.find_todo(id)
    print(request.headers)
    if 'HX-Request' in request.headers:
        return render_template('todo/show_todo.html.j2', todo=todo)
    else:
        todos = db.list_todos()
        return render_template('index.html.j2', todos=todos, current_todo=todo)


@app.route("/todos/new")
def new_todo():
    return render_template('list/new_todo.html.j2')


@app.route("/todos/new/close")
def close_new_todo():
    return render_template('list/new_todo_button.html.j2')


@app.route("/todos", methods=["POST"])
def create_todo():
    todo_name = request.form["name"]
    if not todo_name:
        return "name required", 400
    todo = db.create_todo(todo_name)
    return render_template("list/create_todo.html.j2", todo=todo)


@app.route("/todos/<int:id>", methods=["PATCH"])
def update_todo(id):
    todo_name = request.form["name"]
    if not todo_name:
        return "name required", 400
    todo = db.update_todo(id, todo_name)
    returning_query = json.loads(request.headers["X-DATA"])
    return render_template("update_todo.html.j2",
                           todo=todo,
                           returning_query=returning_query)


@app.route("/todos/<int:id>/edit")
def edit_todo(id):
    todo = db.find_todo(id)
    return render_template("todo/edit_todo.html.j2", todo=todo)


@app.route("/todolist/item/<int:id>/edit")
def edit_todolist_item(id):
    todo = db.find_todo(id)
    return render_template("list/edit_todo.html.j2", todo=todo)


@app.route("/todolist/item/<int:id>/edit/close")
def close_edit_todolist_item(id):
    todo = db.find_todo(id)
    return render_template("list/item.html.j2", todo=todo, render_self=True)


@app.route("/todos/<int:id>/edit/close")
def close_edit_todo(id):
    todo = db.find_todo(id)
    return render_template("todo/todo.html.j2", todo=todo, render_self=True)
