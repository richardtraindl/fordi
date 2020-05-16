

import os

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from . import db
from sqlalchemy import or_, and_
from ordi.auth import login_required
from ordi.models import Termin, Tierhaltung, Person, Tier

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/write', methods=('GET', 'POST'))
@login_required
def write():
    filename = "tblTier.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    file = open(path_and_filename, "r") 
    print(file.readline())
    return render_template('admin/admin.html', page_title="Admin")




