

from datetime import date, timedelta
from operator import attrgetter
import re, os

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, send_file
from werkzeug.exceptions import abort
from sqlalchemy import func, distinct, or_, and_

from . import db
from ordi.auth import login_required
from ordi.models import *
from ordi.reqhelper import *
from ordi.values import *
from ordi.createpdf import *
from ordi.util.helper import *

bp = Blueprint('patient', __name__)


#tierhaltung
@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    familienname = "A"
    tiername = ""
    kunde = True
    patient = True

    if(request.method == 'POST'):
        familienname = request.form['familienname']
        tiername = request.form['tiername']
        if(request.form.get('kunde')):
            kunde = True
        else:
            kunde = False
        if(request.form.get('patient')):
            patient = True
        else:
            patient = False
    
    tierhaltungen = db.session.query(Tierhaltung, Person, Tier) \
        .join(Person, Person.id==Tierhaltung.person_id) \
        .join(Tier, Tier.id==Tierhaltung.tier_id) \
        .filter(Person.familienname.like(familienname + "%"), 
                Tier.tiername.like(tiername + "%"), 
                Person.kunde==kunde, Tier.patient==patient).all() # .limit(500)

    return render_template('patient/index.html', tierhaltungen=tierhaltungen, 
        familienname=familienname, tiername=tiername, kunde=kunde, patient=patient, 
        page_title="Karteikarten")


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    anredewerte = []
    for key, value in ANREDE.items():
        anredewerte.append([key, value])

    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])

    if(request.method == 'POST'):
        person, error = fill_and_validate_person(None, request)
        if(len(error) > 0):
            flash(error)
            tier = Tier()
            return render_template('patient/create.html', 
                person=person, tier=tier, anredewerte=anredewerte, 
                geschlechtswerte=geschlechtswerte, page_title="Neue Karteikarte")

        tier, error = fill_and_validate_tier(None, request)
        if(len(error) > 0):
            flash(error)
            return render_template('patient/create.html', 
                person=person, tier=tier, anredewerte=anredewerte, 
                geschlechtswerte=geschlechtswerte, page_title="Neue Karteikarte")

        db.session.add(person)
        db.session.add(tier)
        db.session.commit()

        tierhaltung = Tierhaltung(person_id = person.id, tier_id = tier.id)
        db.session.add(tierhaltung)
        db.session.commit()
        return redirect(url_for('patient.show', id=tierhaltung.id))
    else:
        person = Person()
        tier = Tier()
        return render_template('patient/create.html', person=person, 
            tier=tier, anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, 
            page_title="Neue Karteikarte")


@bp.route('/<int:id>/show', methods=('GET',))
@login_required
def show(id):
    anredewerte = []
    for key, value in ANREDE.items():
        anredewerte.append([key, value])

    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])

    laborreferenzen = []
    for referenz in LABOR_REFERENZ:
        laborreferenzen.append(referenz)

    impfungswerte = []
    for key, value in IMPFUNG.items():
        impfungswerte.append([key, value])

    tierhaltung = db.session.query(Tierhaltung).filter(Tierhaltung.id == id).first()
    behandlungen = db.session.query(Behandlung) \
        .filter(Behandlung.tier_id == tierhaltung.tier.id) \
        .order_by(Behandlung.id.asc()).all()
    datum = datetime.today()
    datum_ende = datum + timedelta(days=7)

    termin = db.session.query(Termin) \
               .filter(and_(Termin.tierhaltung_id==id, Termin.ende >= datum)).first()

    return render_template('patient/tierhaltung.html', tierhaltung=tierhaltung, 
        termin=termin, behandlungen=behandlungen, datum=datum.strftime("%d.%m.%Y"), 
        anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, 
        laborreferenzen=laborreferenzen, impfungswerte=impfungswerte, page_title="Karteikarte")


@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id):
    tierhaltung = db.session.query(Tierhaltung).get(id)
    if(tierhaltung):
        if(db.session.query(Tierhaltung).filter(Tierhaltung.person_id == tierhaltung.person_id).count() == 1):
            person = db.session.query(Person).get(tierhaltung.person_id)
        else:
            person = None

        if(db.session.query(Tierhaltung).filter(Tierhaltung.tier_id == tierhaltung.tier_id).count() == 1):
            tier = db.session.query(Tier).get(tierhaltung.tier_id)
        else:
            tier = None

        termine = db.session.query(Termin).filter(Termin.tierhaltung_id == tierhaltung.id).all()
        for termin in termine:
            db.session.delete(termin)
        db.session.commit()

        db.session.delete(tierhaltung)
        db.session.commit()

        if(person):
            db.session.delete(person)
            db.session.commit()

        if(tier):
            db.session.delete(tier)
            db.session.commit()

    return redirect(url_for('patient.index'))
# tierhaltung


# tier
@bp.route('/<int:id>/create_tier', methods=('GET', 'POST'))
@login_required
def create_tier(id):
    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])

    if(request.method == 'POST'):
        tier, error = fill_and_validate_tier(None, request)
        if(len(error) > 0):
            flash(error)
            return render_template('patient/create_tier.html', tier=None, 
                geschlechtswerte=geschlechtswerte, page_title="Neues Tier")

        db.session.add(tier)
        db.session.commit()

        tierhaltung = Tierhaltung.query.get(id)
        new_tierhaltung = Tierhaltung(person_id=tierhaltung.person_id, tier_id = tier.id)
        db.session.add(new_tierhaltung)
        db.session.commit()
        return redirect(url_for('patient.show', id=new_tierhaltung.id))
    else:
        tier = Tier()
        return render_template('patient/create_tier.html', tier=tier, 
            geschlechtswerte=geschlechtswerte, page_title="Neues Tier")


@bp.route('/<int:id>/<int:tier_id>/edit_tier', methods=('GET', 'POST'))
@login_required
def edit_tier(id, tier_id):
    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])

    if(request.method == 'POST'):
        tier = db.session.query(Tier).get(tier_id)
        tier, error = fill_and_validate_tier(tier, request)
        if(len(error) > 0):
            flash(error)
            return render_template('patient/edit_tier.html', id=id, tier=tier, 
                geschlechtswerte=geschlechtswerte, page_title="Tier ändern")
        else:
            db.session.commit()
            return redirect(url_for('patient.show', id=id))
    else:
        tier = db.session.query(Tier).get(tier_id)
        return render_template('patient/edit_tier.html', id=id, tier=tier, 
            geschlechtswerte=geschlechtswerte, page_title="Tier ändern")
# tier


# person
@bp.route('/<int:id>/<int:person_id>/edit_person', methods=('GET', 'POST'))
@login_required
def edit_person(id, person_id):
    anredewerte = []
    for key, value in ANREDE.items():
        anredewerte.append([key, value])

    if(request.method == 'POST'):
        person = db.session.query(Person).get(person_id)
        person, error = fill_and_validate_person(person, request)
        if(len(error) > 0):
            flash(error)
            return render_template('patient/edit_person.html', id=id, person=person, 
                anredewerte=anredewerte, page_title="Person ändern")

        db.session.commit()

        return redirect(url_for('patient.show', id=id))

    person = db.session.query(Person).get(person_id)

    return render_template('patient/edit_person.html', id=id, person=person, 
        anredewerte=anredewerte, page_title="Person ändern")
# person


# behandlung
def save_or_delete_impfungen(behandlung, impfungstexte):
    #impfungen = db.session.query(Impfung).filter(Impfung.behandlung_id==behandlung_id).all()
    for impfungstext in impfungstexte:
        try:
            impfungscode = IMPFUNG[impfungstext]
        except:
            print("severe error")
            cursor.close()
            return False
        found = False
        for impfung in behandlung.impfungen:
            if(impfungscode == impfung.impfungscode):
                found = True
                break
        if(found == False):
            new_impfung = Impfung(behandlung_id=behandlung.id, impfungscode=impfungscode)
            db.session.add(new_impfung)
    db.session.commit()

    for impfung in behandlung.impfungen:
        found = False
        for impfungstext in impfungstexte:
            impfungscode = IMPFUNG[impfungstext]
            if(impfungscode == impfung.impfungscode):
                found = True
                break
        if(found == False):
            db.session.delete(impfung)
    db.session.commit()

    return True


@bp.route('/<int:id>/save_behandlungen', methods=('GET', 'POST'))
@login_required
def save_behandlungen(id):
    if(request.method == 'POST'):
        tierhaltung = Tierhaltung.query.get(id)

        behandlungen = db.session.query(Behandlung) \
                        .filter(Behandlung.tier_id == tierhaltung.tier.id) \
                        .order_by(Behandlung.id.asc()).all()

        datum=datetime.today()
        termin = db.session.query(Termin) \
                        .filter(and_(Termin.tierhaltung_id==id, Termin.ende >= datum)).first()

        reqbehandlungen = build_behandlungen(request)
        for reqbehandlung in reqbehandlungen:
            behandlung = None
            if(len(reqbehandlung['behandlung_id']) > 0):
                try:
                    behandlung_id = int(reqbehandlung['behandlung_id'])
                    behandlung = db.session.query(Behandlung).get(behandlung_id)
                except:
                    behandlung_id = None
                    behandlung = None

            behandlung, str_impfungen, error = fill_and_validate_behandlung(behandlung, reqbehandlung)
            if(len(error) > 0):
                flash(error)

                #####################
                # Bahndlungen aus Datenbank mit jenen des Request mergen
                mergedbehandlungen = []

                for behandlung in behandlungen:
                    found = False
                    for reqbehandlung in reqbehandlungen:
                        if(len(reqbehandlung['behandlung_id']) > 0):
                            try:
                                behandlung_id = int(reqbehandlung['behandlung_id'])
                            except:
                                continue
                            if(behandlung.id == behandlung_id):
                                mergedbehandlungen.append(reqbehandlung)
                                found = True
                                break
                    if(found == False):
                        mergedbehandlungen.append(behandlung)

                for reqbehandlung in reqbehandlungen:
                    if(len(reqbehandlung['behandlung_id']) == 0):
                        mergedbehandlungen.append(reqbehandlung)
                #####################

                anredewerte = []
                for key, value in ANREDE.items():
                    anredewerte.append([key, value])

                geschlechtswerte = []
                for key, value in GESCHLECHT.items():
                    geschlechtswerte.append([key, value])

                laborreferenzen = []
                for referenz in LABOR_REFERENZ:
                    laborreferenzen.append(referenz)

                impfungswerte = []
                for key, value in IMPFUNG.items():
                    impfungswerte.append([key, value])

                return render_template('patient/tierhaltung.html', tierhaltung=tierhaltung, 
                            termin=termin, behandlungen=mergedbehandlungen, 
                            datum=datum.strftime("%d.%m.%Y"), anredewerte=anredewerte, 
                            geschlechtswerte=geschlechtswerte, laborreferenzen=laborreferenzen, 
                            impfungswerte=impfungswerte, page_title="Karteikarte")

            if(behandlung.id == None):
                behandlung.tier_id = tierhaltung.tier_id
                db.session.add(behandlung)
            db.session.commit()

            if(len(str_impfungen) > 0):
                impfungstexte = str_impfungen.split(',')
            else:
                impfungstexte = []
            save_or_delete_impfungen(behandlung, impfungstexte)

    return redirect(url_for('patient.show', id=id))


@bp.route('/<int:behandlung_id>/delete_behandlung', methods=('GET',))
@login_required
def delete_behandlung(behandlung_id):
    behandlung = db.session.query(Behandlung).get(behandlung_id)
    if(behandlung):
        tierhaltung = db.session.query(Tierhaltung) \
            .filter(Tierhaltung.tier_id==behandlung.tier_id).first()
        db.session.delete(behandlung)
        db.session.commit()
        return redirect(url_for('patient.show', id=tierhaltung.id))
    else:
        flash("Fehler beim Löschen der Behandlung: " + str(behandlung_id))
        return redirect(url_for('patient.index'))


@bp.route('/<int:behandlung_id>/async_delete_behandlung', methods=('GET',))
@login_required
def async_delete_behandlung(behandlung_id):
    behandlung = db.session.query(Behandlung).get(behandlung_id)
    if(behandlung):
        db.session.delete(behandlung)
        db.session.commit()
        return "OK"
    return ""


@bp.route('/<int:behandlung_id>/async_read_behandlung', methods=('GET',))
@login_required
def async_read_behandlung(behandlung_id):
    print(behandlung_id)
    behandlung = db.session.query(Behandlung).get(behandlung_id)
    if(behandlung):
        str_impfungen = ""
        for impfung in behandlung.impfungen:
            if(len(str_impfungen) > 0):
                str_impfungen += ","
            str_impfungen += reverse_lookup(IMPFUNG, impfung.impfungscode)

        return { 'datum' : behandlung.datum.strftime("%d.%m.%Y"),
                 'gewicht' : behandlung.gewicht,
                 'diagnose' : behandlung.diagnose,
                 'laborwerte1' : behandlung.laborwerte1,
                 'laborwerte2' : behandlung.laborwerte2,
                 'arzneien' : behandlung.arzneien,
                 'arzneimittel' : behandlung.arzneimittel,
                 'impfungen' : str_impfungen }
    return {}
# behandlung

