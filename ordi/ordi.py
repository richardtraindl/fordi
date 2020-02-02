

from datetime import date
import re, os

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, send_file
from werkzeug.exceptions import abort

from . import db
from ordi.auth import login_required
from ordi.models import *
from ordi.dbaccess import *
from ordi.reqhelper import *
from ordi.values import *
from ordi.createpdf import *

bp = Blueprint('ordi', __name__)


#tierhaltung
@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    familienname = ""
    tiername = ""
    kunde = 1
    patient = 1
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
        .join(Person, Tierhaltung.person_id == Person.id) \
        .join(Tier, Tierhaltung.tier_id == Tier.id).filter(Person.familienname.like(familienname + "%"), Tier.tiername.like(tiername + "%"), Person.kunde==kunde, Tier.patient==patient).all()
    return render_template('ordi/tierhaltungen.html', familienname=familienname, tiername=tiername, kunde=kunde, patient=patient, tierhaltungen=tierhaltungen, page_title="Karteikarten")


@bp.route('/create_tierhaltung', methods=('GET', 'POST'))
@login_required
def create_tierhaltung():
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
            return render_template('ordi/create_tierhaltung.html', person=person, tier=None, anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, new="true", page_title="Neue Karteikarte")

        tier, error = fill_and_validate_tier(None, request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/create_tierhaltung.html')
            return render_template('ordi/create_tierhaltung.html', person=person, tier=tier, anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, new="true", page_title="Neue Karteikarte")

        db.session.add(person)
        db.session.commit()

        db.session.add(tier)
        db.session.commit()

        adresse = fill_and_validate_adresse(None, request)[0]
        if(len(adresse.strasse) > 0 or len(adresse.postleitzahl) > 0 or len(adresse.ort) > 0):
            #adresse.person_id=person.id
            db.session.add(adresse)
            db.session.commit()

        kontakte = fill_and_validate_kontakte([], request)[0]
        for kontakt in kontakte:
            if(len(kontakt.kontakt) > 0):
                #kontakt.person_id=person.id
                db.session.add(kontakt)
                db.session.commit()

        tierhaltung = Tierhaltung(person_id = person.id, tier_id = tier.id)
        db.session.add(tierhaltung.tier_id)
        db.session.commit()
        return redirect(url_for('ordi.show_tierhaltung', id=tierhaltung.id))
    else:
        return render_template('ordi/create_tierhaltung.html', person=None, tier=None, anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, new="true", page_title="Neue Karteikarte")


@bp.route('/<int:id>/show_tierhaltung', methods=('GET',))
@login_required
def show_tierhaltung(id):
    tierhaltung = db.session.query(Tierhaltung, Person, Tier) \
        .join(Person, Tierhaltung.person_id == Person.id) \
        .join(Tier, Tierhaltung.tier_id == Tier.id).filter(Tierhaltung.id==id).first()
    adresse = db.session.query(Adresse).filter(Adresse.person_id==tierhaltung.Person.id).first()
    kontakte = db.session.query(Kontakt).filter(Kontakt.person_id==tierhaltung.Person.id).all()
    behandlungen = db.session.query(Behandlung).filter(Behandlung.tier_id==tierhaltung.Tier.id).all()

    datum = date.today().strftime("%Y-%m-%d")

    laboreferenzen = []
    for referenz in LABOR_REFERENZ:
        laboreferenzen.append(referenz)

    impfungswerte = []
    for key, value in IMPFUNG.items():
        impfungswerte.append([key, value])

    anredewerte = []
    for key, value in ANREDE.items():
        anredewerte.append([key, value])

    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])
    return render_template('ordi/tierhaltung.html', id=id, tierhaltung=tierhaltung, 
                           adresse=adresse, kontakte=kontakte,
                           behandlungen=behandlungen, datum=datum, 
                           anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, 
                           laboreferenzen=laboreferenzen, impfungswerte=impfungswerte, 
                           page_title="Karteikarte")


@bp.route('/<int:id>/delete_tierhaltung', methods=('GET',))
@login_required
def delete_tierhaltung(id):
    delete_db_tierhaltung(id)
    return redirect(url_for('ordi.index'))
# tierhaltung


# tier
@bp.route('/<int:id>/create_tier', methods=('GET', 'POST'))
@login_required
def create_tier(id):
    if(request.method == 'POST'):
        tier, error = fill_and_validate_tier(None, request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/create_tier.html', id=id)
        db.session.add(tier)
        db.session.commit()

        tierhaltung = Tierhaltung.query.get(id)
        new_tierhaltung = Tierhaltung(person_id=tierhaltung.person_id, tier_id = tier.id)
        db.session.add(new_tierhaltung)
        db.session.commit()
        return redirect(url_for('ordi.show_tierhaltung', id=new_tierhaltung.id))

    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])
    return render_template('ordi/create_tier.html', geschlechtswerte=geschlechtswerte, new="true", page_title="Neues Tier")


@bp.route('/<int:id>/<int:tier_id>/edit_tier', methods=('GET', 'POST'))
@login_required
def edit_tier(id, tier_id):
    if(request.method == 'POST'):
        tier = db.session.query(Tier).get(tier_id)
        tier, error = fill_and_validate_tier(tier, request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/edit_tier.html', id=id, tier_id=tier_id)
        db.session.commit()
        return redirect(url_for('ordi.show_tierhaltung', id=id))

    ctierhaltung, cperson, ctier = read_tierhaltung(id)
    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])
    return render_template('ordi/edit_tier.html', id=id, tier=ctier, geschlechtswerte=geschlechtswerte, page_title="Tier ändern")
# tier


# person
@bp.route('/<int:id>/<int:person_id>/edit_person', methods=('GET', 'POST'))
@login_required
def edit_person(id, person_id):
    if(request.method == 'POST'):
        person = db.session.query(Person).get(person_id)
        person, error = fill_and_validate_person(person, request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/edit_person.html', id=id, person_id=person_id)
        db.session.commit()

        adresse = db.session.query(Adresse).filter(Adresse.person_id==person_id).first()
        adresse = fill_and_validate_adresse(adresse, request)[0]
        if(len(adresse.strasse) > 0 or len(adresse.postleitzahl) > 0 or len(adresse.ort) > 0):
            if(adresse.id == None):
                db.session.add(adresse)
        else:
            if(adresse.id):
                db.session.delete(adresse)
        db.session.commit()

        kontakte = db.session.query(Kontakt).filter(Kontakt.person_id==person_id).all()
        kontakte = fill_and_validate_kontakte(kontakte, request)[0]
        for kontakt in kontakte:
            if(len(kontakt.kontakt) > 0):
                if(kontakt.id == None):
                    db.session.add(kontakt)
            else:
                if(kontakt.id):
                    db.session.delete(kontakt)
        db.session.commit()

        return redirect(url_for('ordi.show_tierhaltung', id=id))

    ctierhaltung, cperson, ctier = read_tierhaltung(id)
    cperson.adresse = read_adresse_for_person(cperson.id)
    cperson.kontakte = read_kontakte_for_person(cperson.id)
    anredewerte = []
    for key, value in ANREDE.items():
        anredewerte.append([key, value])
    return render_template('ordi/edit_person.html', id=id, person=cperson, anredewerte=anredewerte, page_title="Person ändern")
# person


# behandlung
def save_or_delete_impfungen(behandlung_id, impfungstexte):
    impfungen = db.session.query(Impfung).filter(Impfung.behandlung_id==behandlung_id).all()
    for impfungstext in impfungstexte:
        try:
            impfungscode = IMPFUNG[impfungstext]
        except:
            print("severe error")
            cursor.close()
            return False
        found = False
        for impfung in impfungen:
            if(impfungscode == impfung.impfungscode):
                found = True
                break
        if(found == False):
            new_impfung = Impfung(behandlung_id=behandlung_id, impfungscode=impfungscode)
            db.session.add(new_impfung)
            db.session.commit()

    for impfung in impfungen:
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

@bp.route('/<int:id>/save_behandlung', methods=('GET', 'POST'))
@login_required
def save_behandlung(id):
    if(request.method == 'POST'):
        try:
            behandlung_id = int(request['behandlung_id'])
            behandlung = db.session.query(Behandlung).get(behandlung_id)
        except:
            behandlung_id = None
            behandlung = None

        behandlung = fill_and_validate_behandlung(behandlung, request)[0]
        if(behandlung.id):
            db.session.commit()
        elif(len(behandlung.gewicht) > 0 or
             len(behandlung.diagnose) > 0 or
             len(behandlung.laborwerte1) > 0 or
             len(behandlung.laborwerte2) > 0 or
             len(behandlung.arzneien) > 0 or
             len(behandlung.arzneimittel) > 0 or
             len(behandlung.impfungen_extern) > 0):
            tierhaltung = db.session.query(Tierhaltung).get(id)
            behandlung.tier_id = tierhaltung.tier_id
            db.session.add(behandlung)
            db.session.commit()

        if(len(behandlung.impfungen_extern) > 0):
            impfungstexte = behandlung.impfungen_extern.split(',')
        else:
            impfungstexte = []
        save_or_delete_impfungen(behandlung.id, impfungstexte)
    return redirect(url_for('ordi.show_tierhaltung', id=id))
    

@bp.route('/<int:id>/<int:behandlung_id>/delete_behandlung', methods=('GET',))
@login_required
def delete_behandlung(id, behandlung_id):
    delete_db_behandlung(behandlung_id)
    return redirect(url_for('ordi.show_tierhaltung', id=id))
# behandlung


# behandlungsverlauf
@bp.route('/behandlungsverlaeufe', methods=('GET', 'POST'))
@login_required
def behandlungsverlaeufe():
    if(request.method == 'POST'):
        try:
            behandlungsjahr = int(request.form['behandlungsjahr'])
        except:
            behandlungsjahr = None
    else:
        behandlungsjahr = None
    behandlungsverlaeufe = read_behandlungsverlaeufe(behandlungsjahr)
    if(behandlungsjahr):
        str_behandlungsjahr = str(behandlungsjahr)
    else:
        str_behandlungsjahr = ""
    return render_template('ordi/behandlungsverlaeufe.html', behandlungsverlaeufe=behandlungsverlaeufe, behandlungsjahr=str_behandlungsjahr, page_title="Behandlungsverläufe")


def dlbehandlungsverlauf(behandlungsverlauf_id):
    cbehandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
    ctierhaltung, cperson, ctier = read_tierhaltung_by_children(cbehandlungsverlauf.person_id, cbehandlungsverlauf.tier_id)
    cperson.adresse = read_adresse_for_person(cperson.id)
    html = render_template('ordi/prints/print_behandlungsverlauf.html', behandlungsverlauf=cbehandlungsverlauf, person=cperson, tier=ctier)
    filename = str(cbehandlungsverlauf.id) + "_behandlungsverlauf_fuer_" + cperson.familienname + "_" + cperson.vorname + ".pdf"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
    html2pdf(html, path_and_filename)
    return path_and_filename

@bp.route('/<int:id>/create_behandlungsverlauf', methods=('GET', 'POST'))
@login_required
def create_behandlungsverlauf(id):
    ctierhaltung, cperson, ctier = read_tierhaltung(id)
    cperson.adresse = read_adresse_for_person(ctierhaltung.person_id)
    cperson.kontakte = read_kontakte_for_person(cperson.id)

    if(request.method == 'POST'):
        cbehandlungsverlauf, error = fill_and_validate_behandlungsverlauf(request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/behandlungsverlauf.html', id=id, behandlungsverlauf= None, person=cperson, tier=ctier, page_title="Behandlungsverlauf")

        cbehandlungsverlauf.person_id = cperson.id
        cbehandlungsverlauf.tier_id = ctier.id
        write_behandlungsverlauf(cbehandlungsverlauf)
        return redirect(url_for('ordi.edit_behandlungsverlauf', behandlungsverlauf_id=cbehandlungsverlauf.id))
    else:
        datum = date.today().strftime("%Y-%m-%d")
        return render_template('ordi/behandlungsverlauf.html', id=id, behandlungsverlauf= None, person=cperson, tier=ctier, datum=datum, page_title="Behandlungsverlauf")


@bp.route('/<int:behandlungsverlauf_id>/edit_behandlungsverlauf', methods=('GET', 'POST'))
@login_required
def edit_behandlungsverlauf(behandlungsverlauf_id):
    cbehandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
    ctierhaltung, cperson, ctier = read_tierhaltung_by_children(cbehandlungsverlauf.person_id, cbehandlungsverlauf.tier_id)
    cperson.adresse = read_adresse_for_person(cperson.id)
    cperson.kontakte = read_kontakte_for_person(cperson.id)
    if(request.method == 'POST'):
        cbehandlungsverlauf, error = fill_and_validate_behandlungsverlauf(request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=cbehandlungsverlauf, 
                                    person=cperson, tier=ctier, page_title="Behandlungsverlauf")

        cbehandlungsverlauf.person_id = cperson.id
        cbehandlungsverlauf.tier_id = ctier.id
        update_behandlungsverlauf(cbehandlungsverlauf)
        path_and_filename = dlbehandlungsverlauf(behandlungsverlauf_id)
        return send_file(path_and_filename, as_attachment=True)
    else:
        return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=cbehandlungsverlauf, 
                                person=cperson, tier=ctier, page_title="Behandlungsverlauf")


@bp.route('/<int:behandlungsverlauf_id>/delete_behandlungsverlauf', methods=('GET',))
@login_required
def delete_behandlungsverlauf(behandlungsverlauf_id):
    delete_db_behandlungsverlauf(behandlungsverlauf_id)
    return redirect(url_for('ordi.behandlungsverlaeufe'))
# behandlungsverlauf


#rechnung
@bp.route('/rechnungen', methods=('GET', 'POST'))
@login_required
def rechnungen():
    if(request.method == 'POST'):
        try:
            rechnungsjahr = int(request.form['rechnungsjahr'])
        except:
            rechnungsjahr = None
    else:
        rechnungsjahr = None
    rechnungen = read_rechnungen(rechnungsjahr)
    if(rechnungsjahr):
        str_rechnungsjahr = str(rechnungsjahr)
    else:
        str_rechnungsjahr = ""
    return render_template('ordi/rechnungen.html', rechnungen=rechnungen, rechnungsjahr=str_rechnungsjahr, page_title="Rechnungen")


def dlrechnung(rechnung_id):
    crechnung = read_rechnung(rechnung_id)
    crechnung.rechnungszeilen = read_rechnungszeilen_for_rechnung(crechnung.id)
    ctierhaltung, cperson, ctier = read_tierhaltung_by_children(crechnung.person_id, crechnung.tier_id)
    cperson.adresse = read_adresse_for_person(cperson.id)
    html = render_template('ordi/prints/print_rechnung.html', rechnung=crechnung, person=cperson, tier=ctier)
    filename = str(crechnung.id) + "_rechnung_fuer_" + cperson.familienname + "_" + cperson.vorname + ".pdf"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
    html2pdf(html, path_and_filename)
    return path_and_filename

@bp.route('/<int:id>/create_rechnung', methods=('GET', 'POST'))
@login_required
def create_rechnung(id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])

    ctierhaltung, cperson, ctier = read_tierhaltung(id)
    cperson.adresse = read_adresse_for_person(cperson.id)
    cperson.kontakte = read_kontakte_for_person(cperson.id)

    if(request.method == 'POST'):
        crechnung, error = fill_and_validate_rechnung(request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        crechnung.rechnungszeilen, zeilen_error = fill_and_validate_rechnungszeilen(req_rechnungszeilen)
        if(len(error) > 0 or len(zeilen_error) > 0):
            flash(error + zeilen_error)
            return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=req_rechnungszeilen, artikelwerte=artikelwerte, 
                                   id=id, person=cperson, tier=ctier, page_title="Rechnung")

        flag, error = crechnung.calc()
        if(flag == False):
            flash(error)
            return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=req_rechnungszeilen, artikelwerte=artikelwerte, 
                                   id=id, person=cperson, tier=ctier, page_title="Rechnung")

        crechnung.person_id = cperson.id
        crechnung.tier_id = ctier.id
        write_rechnung(crechnung)

        for crechnungszeile in crechnung.rechnungszeilen:
            crechnungszeile.rechnung_id = crechnung.id
            write_rechnungszeile(crechnungszeile)

        return redirect(url_for('ordi.edit_rechnung', rechnung_id=crechnung.id))
    else:
        datum = date.today().strftime("%Y-%m-%d")
        ort = "Wien"
        return render_template('ordi/rechnung.html', rechnung=None, rechnungszeilen=None, datum=datum, ort=ort, artikelwerte=artikelwerte, 
                               id=id, person=cperson, tier=ctier, page_title="Rechnung")


@bp.route('/<int:rechnung_id>/edit_rechnung', methods=('GET', 'POST'))
@login_required
def edit_rechnung(rechnung_id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])

    crechnung = read_rechnung(rechnung_id)
    ctierhaltung,cperson, ctier = read_tierhaltung_by_children(crechnung.person_id, crechnung.tier_id)
    cperson.adresse = read_adresse_for_person(cperson.id)
    cperson.kontakte = read_kontakte_for_person(cperson.id)

    if(request.method == 'POST'):
        crechnung, error = fill_and_validate_rechnung(request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        crechnung.rechnungszeilen, zeilen_error = fill_and_validate_rechnungszeilen(req_rechnungszeilen)
        if(len(error) > 0 or len(zeilen_error) > 0):
            flash(error + zeilen_error)
            return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=req_rechnungszeilen, 
                                    artikelwerte=artikelwerte, id=ctierhaltung.id, person=cperson, tier=ctier, page_title="Rechnung")

        flag, error = crechnung.calc()
        if(flag == False):
            flash(error)
            return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=req_rechnungszeilen, 
                                    artikelwerte=artikelwerte, id=tierhaltung.id, person=cperson, tier=ctier, page_title="Rechnung")

        update_rechnung(crechnung)
        for crechnungszeile in crechnung.rechnungszeilen:
            if(crechnungszeile.id):
                update_rechnungszeile(crechnungszeile)
            else:
                crechnungszeile.rechnung_id = rechnung_id
                write_rechnungszeile(crechnungszeile)

        path_and_filename = dlrechnung(crechnung.id)
        return send_file(path_and_filename, as_attachment=True)
    else:
        crechnung = read_rechnung(rechnung_id)
        crechnung.rechnungszeilen = read_rechnungszeilen_for_rechnung(rechnung_id)
        return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=crechnung.rechnungszeilen, artikelwerte=artikelwerte, 
                               id=ctierhaltung.id, person=cperson, tier=ctier, page_title="Rechnung")


@bp.route('/<int:rechnung_id>/delete_rechnung', methods=('GET',))
@login_required
def delete_rechnung(rechnung_id):
    delete_db_rechnung(rechnung_id)
    return redirect(url_for('ordi.rechnungen'))


@bp.route('/<int:rechnungszeile_id>/delete_rechnungszeile', methods=('GET',))
@login_required
def delete_rechnungszeile(rechnungszeile_id):
    crechnungszeile = read_rechnungszeile(rechnungszeile_id)
    delete_db_rechnungszeile(rechnungszeile_id)
    return redirect(url_for('ordi.edit_rechnung', rechnung_id=crechnungszeile.rechnung_id))
# rechnung


@bp.route('/abfragen', methods=('GET', 'POST'))
@login_required
def abfragen():
    if(request.method == 'POST'):
        print(request.form['abfragecode'])
        try:
            abfragecode = int(request.form['abfragecode'])
        except:
            abfragecode = 0
        abfragekriterium = request.form['abfragekriterium']
    else:
        abfragecode = 0
        abfragekriterium = ""
    abfragen = [] # read_abfragen(abfragekriterium)
    return render_template('ordi/abfragen.html', abfragen=abfragen, abfragekriterium=abfragekriterium, page_title="Abfragen")
