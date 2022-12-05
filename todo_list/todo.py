import os
import sqlite3
from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, jsonify, request, render_template, url_for, flash,
                   redirect)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b069f76cfec2cee250e211170324eea2309483ef09faeaf6'
app.config['SQLALCHEMY_DATABASE_URI'] = \
           'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean(), default=False)
    created = db.Column(db.DateTime(), default=date.today())
    deadline = db.Column(db.DateTime(), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'status': self.status,
            'created': self.created,
            'deadline': self.deadline,
        }

@app.route("/todos")
def list_todos():
    where = []
    order_by = []
    if status := request.args.get('status'):
        try: 
            status = int(status)
        except ValueError:
            return 'Invalid status', 400
        else:
            where.append(Todo.status == status)

    if date_from := request.args.get('date_from'):
        date_from = datetime.strptime(date_from,"%Y-%m-%d")
        where.append(Todo.created >= date_from)

    if date_to := request.args.get('date_to'):
        date_to = datetime.strptime(date_to,"%Y-%m-%d")
        where.append(Todo.created <= date_to)

    order_by_param = request.args.get('order_by', 'urgency+')
    if order_by_param[:-1] == 'urgency':
        if order_by_param[-1] == "-":
            order_by.append(Todo.deadline.asc())
        else:
            order_by.append(Todo.deadline.desc())
    
    query = db.session.query(Todo).where(*where).order_by(*order_by).all()
    if count := request.args.get('count'):
        try: 
            count = int(count)
        except ValueError:
            pass
        else:
            query = query.limit(count)

    todos = [todo.to_dict() for todo in query]
    return render_template('index.html', tasks=todos)


@app.route("/todo", methods = ['GET', 'POST'])
def post_todo():
    if request.method == 'POST':
        todo_id = request.form.get('id')
        todo_text = request.form.get('text')

        if not todo_id:
            flash('Name is required!')
        elif not todo_text:
            flash('Text is required!')

        else:
            if deadline := request.form.get('deadline'):
                deadline = datetime.strptime(deadline,"%Y-%m-%d")
            else:
                deadline = None

            todo = Todo(
                    id=todo_id,
                    text=todo_text,
                    deadline=deadline
                    )
            db.session.add(todo)
            db.session.commit()
            return redirect(url_for('list_todos'))

    return render_template('create.html')


@app.route("/todos/<todo_id>",  methods = ['POST'])
def delete_todo(todo_id):
    todo = Todo.query.where(Todo.id==todo_id).first()
    if not todo:
        return "Todo not found", 404
    db.session.delete(todo)
    db.session.commit()
    # return todos list
    query = Todo.query.all()
    todos = [todo.to_dict() for todo in query]
    return render_template('index.html', tasks=todos)


@app.route("/todos/<todo_id>/set_status", methods = ['POST'])
def set_status(todo_id):
    todo = Todo.query.where(Todo.id==todo_id).first()
    if not todo:
        return "Todo not found", 404
    if 'set-done' in request.form:
        todo.status = 1
    else:
        todo.status = 0
    db.session.commit()
    return '', 204


@app.route("/todos/most-urgent")
def list_most_urgent():
    todo = Todo.query.where().order_by(Todo.deadline.desc()).first()
    return jsonify(todo.to_dict())


if __name__ == "__main__":
    app.run()