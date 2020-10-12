import sqlite3
import time

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))    

def init_admin(username, password, firstname, lastname, number, email):
    db = get_db()
    db.execute(
        'INSERT INTO user (username, password, firstname, lastname, number, email, admin) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (username, generate_password_hash(password), firstname, lastname, number, email, 1)
    )
    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    init_admin('admin', 'admin', 'Kamron', 'Ali', '07508237386', 'kamronali@protonmail.com')
    click.echo('Initialized the database')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)