"""
Simple Flask Todo Application
Defaults to use local sqlite db
MYSQL_* environment variables can be defined to use external mysql db
"""

import os
import platform
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
details = {
    'provider': platform.node(),
    'region': os.getenv('REGION', default = 'My')
}

# Cheeck for external mysql backend database
if os.getenv('MYSQL_HOST'):
    mysql_host =  os.getenv('MYSQL_HOST')
    mysql_user = os.getenv('MYSQL_USER')
    mysql_pass = os.getenv('MYSQL_PASSWORD')
    mysql_db = os.getenv('MYSQL_DATABASE')
    DB_CONN = f"mysql+mysqlconnector://{mysql_user}:{mysql_pass}@{mysql_host}/{mysql_db}"
else:
    # /// = relative path, //// = absolute path
    DB_CONN = 'sqlite:///db.sqlite'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONN
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Todo(db.Model): # pylint: disable=too-few-public-methods
    """todo class representing task list item"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)

@app.route("/add", methods=["POST"])
def add():
    """method to add task item to db then redirect to home"""
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    """method to update task item then redirect to home"""
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    """method to delete task item from db then redirect to home"""
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/host")
def host():
    """page which returns string"""
    return f'Hosted By: {details.get("provider")}\n'

@app.route("/")
def home():
    """home page to return todo list"""
    todo_list = Todo.query.all()
    return render_template("base.html", todo_list=todo_list, details=details)

if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", port=8080, debug=True)
