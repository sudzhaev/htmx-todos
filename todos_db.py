import sqlite3


class CustomRow(sqlite3.Row):
    def status(self):
        status = self['status']
        if status == 0:
            return 'new'
        elif status == 1:
            return 'on it'
        elif status == 2:
            return 'done'
        else:
            raise Exception()

    def __getattr__(self, name):
        if name in self.keys():
            return self[name]
        else:
            raise AttributeError(f"'CustomRow' object has no attribute '{name}'")


def con():
    connection = sqlite3.connect("todos.db", isolation_level=None)
    connection.row_factory = CustomRow
    return connection


def cursor():
    return con().cursor()


def init():
    cur = cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id integer PRIMARY KEY AUTOINCREMENT, 
            name text NOT NULL
        )
        """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todos(
            id integer PRIMARY KEY AUTOINCREMENT, 
            name text NOT NULL,
            status integer NOT NULL,
            assignee_id integer,
            FOREIGN KEY (assignee_id) REFERENCES users(id)
        )
        """)


def list_todos():
    return cursor().execute("SELECT id, name, status FROM todos").fetchall()


def create_todo(name):
    return cursor().execute("""
        INSERT INTO todos (name, status, assignee_id)
        VALUES (?, 0, NULL)
        RETURNING id, name, status, assignee_id
    """, (name,)).fetchone()


def update_todo(id, name):
    return cursor().execute("""
        UPDATE todos SET name = ?
        WHERE id = ?
        RETURNING id, name, status, assignee_id
    """, (name, id)).fetchone()


def find_todo(id):
    return cursor().execute("""
        SELECT id, name, status
        FROM todos
        WHERE id = ?
    """, (id,)).fetchone()


def destroy_todo(id):
    return cursor().execute("""
        DELETE FROM todos WHERE id = ?
    """, (id,))
