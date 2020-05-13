

from datetime import date, timedelta
import os

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, send_file
from werkzeug.exceptions import abort
from sqlalchemy import func, distinct, or_, and_

from . import db
from ordi.auth import login_required
from ordi.models import *
from ordi.reqhelper import *
from ordi.values import *
from ordi.createpdf import *

bp = Blueprint('behandlungsverlauf', __name__, url_prefix='/behandlungsverlauf')


@bp.route('/index', methods=('GET', 'POST'))
@login_required
def index():
    if(request.method == 'POST'):
        try:
            behandlungsjahr = int(request.form['behandlungsjahr'])
        except:
            behandlungsjahr = None
    else:
        behandlungsjahr = None

    if(behandlungsjahr):
        begin = str(behandlungsjahr - 1) + "-12-31"
        end = str(behandlungsjahr + 1) + "-01-01"
        behandlungsverlaeufe = db.session.query(Behandlungsverlauf, Person, Tier) \
            .join(Person, Behandlungsverlauf.person_id == Person.id) \
            .join(Tier, Behandlungsverlauf.tier_id == Tier.id).filter(Behandlungsverlauf.datum > begin, Behandlungsverlauf.datum < end).all()
    else:
        behandlungsverlaeufe = db.session.query(Behandlungsverlauf, Person, Tier) \
            .join(Person, Behandlungsverlauf.person_id == Person.id) \
            .join(Tier, Behandlungsverlauf.tier_id == Tier.id).all()

    if(behandlungsjahr):
        str_behandlungsjahr = str(behandlungsjahr)
    else:
        str_behandlungsjahr = ""

    return render_template('behandlungsverlauf/index.html', behandlungsverlaeufe=behandlungsverlaeufe, 
        behandlungsjahr=str_behandlungsjahr, page_title="Behandlungsverläufe")


def dl_behandlungsverlauf(behandlungsverlauf_id):
    behandlungsverlauf = db.session.query(Behandlungsverlauf).get(behandlungsverlauf_id)

    html = render_template('behandlungsverlauf/print.html', behandlungsverlauf=behandlungsverlauf)

    filename = str(behandlungsverlauf.id) + "_behandlungsverlauf_fuer_" + behandlungsverlauf.person.familienname + \
        "_" + behandlungsverlauf.person.vorname + ".pdf"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)

    html2pdf(html, path_and_filename)

    return path_and_filename

@bp.route('/<int:id>/create', methods=('GET', 'POST'))
@login_required
def create(id):
    tierhaltung = db.session.query(Tierhaltung).get(id)

    datum = date.today().strftime("%d.%m.%Y")

    if(request.method == 'POST'):
        behandlungsverlauf, error = fill_and_validate_behandlungsverlauf(None, request)
        if(len(error) > 0):
            flash(error)
            return render_template('behandlungsverlauf/behandlungsverlauf.html', id=id, 
                person=tierhaltung.person, tier=tierhaltung.tier, 
                behandlungsverlauf=behandlungsverlauf, 
                datum=datum, page_title="Behandlungsverlauf")

        behandlungsverlauf.person_id = tierhaltung.person.id
        behandlungsverlauf.tier_id = tierhaltung.tier.id
        db.session.add(behandlungsverlauf)
        db.session.commit()
        return redirect(url_for('behandlungsverlauf.edit', behandlungsverlauf_id=behandlungsverlauf.id))
    else:
        behandlungsverlauf = Behandlungsverlauf()
        return render_template('behandlungsverlauf/behandlungsverlauf.html', id=id, 
            person=tierhaltung.person, tier=tierhaltung.tier, 
            behandlungsverlauf=behandlungsverlauf, datum=datum, page_title="Behandlungsverlauf")


@bp.route('/<int:behandlungsverlauf_id>/edit', methods=('GET', 'POST'))
@login_required
def edit(behandlungsverlauf_id):
    behandlungsverlauf = db.session.query(Behandlungsverlauf).get(behandlungsverlauf_id)

    if(request.method == 'POST'):
        behandlungsverlauf, error = fill_and_validate_behandlungsverlauf(behandlungsverlauf, request)
        if(len(error) > 0):
            flash(error)
            return render_template('behandlungsverlauf/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, 
                page_title="Behandlungsverlauf")

        db.session.commit()
        path_and_filename = dl_behandlungsverlauf(behandlungsverlauf_id)
        return send_file(path_and_filename, as_attachment=True)
    else:
        return render_template('behandlungsverlauf/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, 
            page_title="Behandlungsverlauf")


@bp.route('/<int:behandlungsverlauf_id>/delete', methods=('GET',))
@login_required
def delete(behandlungsverlauf_id):
    behandlungsverlauf = db.session.query(Behandlungsverlauf).get(behandlungsverlauf_id)
    db.session.delete(behandlungsverlauf)
    db.session.commit()
    return redirect(url_for('behandlungsverlauf.index'))
