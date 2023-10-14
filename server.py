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


def tmpl_data():
    return json.loads(request.headers["X-Tmpl-Data"])


def htmx_request():
    return 'HX-Request' in request.headers

# common endpoints

@app.get("/")
def index():
    todos = db.list_todos()
    return render_template('index.html.j2', todos=todos)


@app.patch("/todos/<int:id>")
def update_todo(id):
    """
    Universal method to update todo from any place of UI.
    Uses 'X-Tmpl-Data' header to render response
    """
    todo_name = request.form["name"]
    if not todo_name:
        return "name required", 400
    todo = db.update_todo(id, todo_name)
    return render_template("update_todo.html.j2",
                           todo=todo,
                           tmpl_data=tmpl_data())


@app.delete("/todos/<int:id>")
def destroy_todo(id):
    db.destroy_todo(id)
    return render_template("destroy_todo.html.j2",
                           todo_id=id,
                           tmpl_data=tmpl_data())

# todolist endpoints

@app.get("/todolist/item/<int:id>")
def show_todolist_item(id):
    todo = db.find_todo(id)
    print(request.headers)
    if htmx_request():
        return render_template('todo/show_todo.html.j2', todo=todo)
    else:
        todos = db.list_todos()
        return render_template('index.html.j2', todos=todos, current_todo=todo)


@app.get("/todolist/item/new")
def new_todolist_item():
    return render_template('list/new_todo.html.j2')


@app.get("/todolist/item/new/close")
def close_new_todolist_item():
    return render_template('list/new_todo_button.html.j2')


@app.post("/todolist/item")
def create_todolist_item():
    todo_name = request.form["name"]
    if not todo_name:
        return "name required", 400
    todo = db.create_todo(todo_name)
    return render_template("list/create_todo.html.j2", todo=todo)


@app.get("/todolist/item/<int:id>/edit")
def edit_todolist_item(id):
    todo = db.find_todo(id)
    return render_template("list/edit_todo.html.j2", todo=todo)


@app.get("/todolist/item/<int:id>/edit/close")
def close_edit_todolist_item(id):
    todo = db.find_todo(id)
    return render_template("list/item.html.j2", todo=todo, render_self=True)

# todo endpoints

@app.get("/todos/<int:id>/edit")
def edit_todo(id):
    todo = db.find_todo(id)
    return render_template("todo/edit_todo.html.j2", todo=todo)


@app.get("/todos/<int:id>/edit/close")
def close_edit_todo(id):
    todo = db.find_todo(id)
    return render_template("todo/todo.html.j2", todo=todo, render_self=True)
