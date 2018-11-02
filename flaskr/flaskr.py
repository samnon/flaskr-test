# all the imports
import os
import sqlite3
import pdb
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='admin'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text, id from entries order by id desc')
    cur2 = db.execute('select name,startTime,endTime, id from doctors order by id desc')
    doctors = cur2.fetchall()
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries, doctors=doctors)


@app.route('/manage')
def manage_entries():
    db = get_db()
    cur = db.execute('select title, text, id from entries order by id desc')
    cur2 = db.execute('select name,startTime,endTime, id from doctors order by id desc')
    doctors = cur2.fetchall()
    entries = cur.fetchall()
    return render_template('manage.html', entries=entries, doctors=doctors)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(100)
    db = get_db()
    if request.form['title'].strip() and request.form['text'].strip:
        db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
        db.commit()
    return redirect(url_for('manage_entries'))


@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    if request.form['name'].strip() and request.form['startTime'] and request.form['endTime']:
        db.execute('insert into doctors (name,startTime,endTIme) values(?,?,?)', [request.form['name'].strip(), request.form['startTime'],request.form['endTime']])
        db.commit()
        flash('New Doctor was successfully posted')
    return redirect(url_for('manage_entries'))


@app.route('/delete', methods=['GET', 'POST'])
def delete_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('delete from entries where id=' + request.args.get("id", 0, type=str))
    db.commit()
    return redirect(url_for('manage_entries'))


@app.route('/deleteDoctor', methods=['GET', 'POST'])
def delete_doctor():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('delete from doctors where id=' + request.args.get("id", 0, type=str))
    db.commit()
    return redirect(url_for('manage_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('manage_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
