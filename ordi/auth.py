
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
import click

from . import db
from ordi.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.cli.command("register")
@click.argument("username")
@click.argument("password")
def register(username, password):
    error = None

    if(not username):
        error = 'Username is required.'
    elif(not password):
        error = 'Password is required.'
    else:
        user = db.session.query(User).filter(User.username == username).scalar()
        if(user):
            error = 'User {} is already registered.'.format(username)

        if(error is None):
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            print("user registered")
        else:
            print(error)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        error = None
        user = db.session.query(User).filter(User.username == username).scalar()

        if(user is None):
            error = 'Incorrect username.'
        elif(not check_password_hash(user.password, password)):
            error = 'Incorrect password.'

        if(error is None):
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)
    return render_template('auth/login.html', page_title="Anmelden")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if(user_id is None):
        g.user = None
    else:
        g.user = db.session.query(User).get(user_id)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


