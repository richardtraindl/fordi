

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
            adresse.person_id=person.id
            db.session.add(adresse)
            db.session.commit()

        kontakte = fill_and_validate_kontakte([], request)[0]
        for kontakt in kontakte:
            if(len(kontakt.kontakt) > 0):
                kontakt.person_id=person.id
                db.session.add(kontakt)
                db.session.commit()

        tierhaltung = Tierhaltung(person_id = person.id, tier_id = tier.id)
        db.session.add(tierhaltung)
        db.session.commit()
        return redirect(url_for('ordi.show_tierhaltung', id=tierhaltung.id))
    else:
        return render_template('ordi/create_tierhaltung.html', person=None, tier=None, adresse=None, kontakte=[], anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, new="true", page_title="Neue Karteikarte")


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
    tierhaltung = db.session.query(Tierhaltung).get(id)
    db.session.delete(tierhaltung)
    db.session.commit()
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
    return render_template('ordi/create_tier.html', tier=None, geschlechtswerte=geschlechtswerte, new="true", page_title="Neues Tier")


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

    tier = db.session.query(Tier).get(tier_id)
    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])
    return render_template('ordi/edit_tier.html', id=id, tier=tier, geschlechtswerte=geschlechtswerte, page_title="Tier ändern")
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

    person = db.session.query(Person).get(person_id)
    adresse = db.session.query(Adresse).filter(Adresse.person_id==person_id).first()
    kontakte = db.session.query(Kontakt).filter(Kontakt.person_id==person_id).all()
    anredewerte = []
    for key, value in ANREDE.items():
        anredewerte.append([key, value])
    return render_template('ordi/edit_person.html', id=id, person=person, adresse=adresse, 
                           kontakte=kontakte, anredewerte=anredewerte, page_title="Person ändern")
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

@bp.route('/<int:id>/save_behandlungen', methods=('GET', 'POST'))
@login_required
def save_behandlungen(id):
    if(request.method == 'POST'):
        tierhaltung = Tierhaltung.query.get(id)

        req_behandlungen = build_behandlungen(request)
        for req_behandlung in req_behandlungen:
            behandlung = None
            if(len(req_behandlung['behandlung_id']) > 0):
                try:
                    behandlung_id = int(req_behandlung['behandlung_id'])
                    behandlung = db.session.query(Behandlung).get(behandlung_id)
                except:
                    behandlung_id = None
                    behandlung = None

            behandlung = fill_and_validate_behandlung(behandlung, req_behandlung)[0]
            if(behandlung.id == None):
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
    behandlung = db.session.query(Behandlung).get(behandlung_id)
    db.session.delete(behandlung)
    db.session.commit()
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

    return render_template('ordi/behandlungsverlaeufe.html', behandlungsverlaeufe=behandlungsverlaeufe, behandlungsjahr=str_behandlungsjahr, page_title="Behandlungsverläufe")


def dl_behandlungsverlauf(behandlungsverlauf_id):
    behandlungsverlauf = db.session.query(Behandlungsverlauf).get(behandlungsverlauf_id)
    tierhaltung = db.session.query(Tierhaltung, Person, Tier) \
        .join(Person, Tierhaltung.person_id == Person.id) \
        .join(Tier, Tierhaltung.tier_id == Tier.id).filter(Tierhaltung.person_id==behandlungsverlauf.person_id, Tierhaltung.tier_id==behandlungsverlauf.tier_id, ).first()
    adresse = db.session.query(Adresse).filter(Adresse.person_id==tierhaltung.Person.id).first()

    html = render_template('ordi/prints/print_behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, 
                            tierhaltung=tierhaltung, adresse=adresse)

    filename = str(behandlungsverlauf.id) + "_behandlungsverlauf_fuer_" + tierhaltung.Person.familienname + "_" + tierhaltung.Person.vorname + ".pdf"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
    html2pdf(html, path_and_filename)

    return path_and_filename

@bp.route('/<int:id>/create_behandlungsverlauf', methods=('GET', 'POST'))
@login_required
def create_behandlungsverlauf(id):
    tierhaltung = db.session.query(Tierhaltung, Person, Tier) \
        .join(Person, Tierhaltung.person_id == Person.id) \
        .join(Tier, Tierhaltung.tier_id == Tier.id).filter(Tierhaltung.id==id).first()
    adresse = db.session.query(Adresse).filter(Adresse.person_id==tierhaltung.Person.id).first()
    kontakte = db.session.query(Kontakt).filter(Kontakt.person_id==tierhaltung.Person.id).all()

    if(request.method == 'POST'):
        behandlungsverlauf, error = fill_and_validate_behandlungsverlauf(None, request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/behandlungsverlauf.html', id=id, 
                                   behandlungsverlauf=behandlungsverlauf, 
                                   tierhaltung=tierhaltung, adresse=adresse, 
                                   kontakte=kontakte, datum=datum, page_title="Behandlungsverlauf")

        behandlungsverlauf.person_id = tierhaltung.Person.id
        behandlungsverlauf.tier_id = tierhaltung.Tier.id
        db.session.add(behandlungsverlauf)
        db.session.commit()
        return redirect(url_for('ordi.edit_behandlungsverlauf', behandlungsverlauf_id=behandlungsverlauf.id))
    else:
        datum = date.today().strftime("%Y-%m-%d")
        return render_template('ordi/behandlungsverlauf.html', id=id, 
                               behandlungsverlauf=None, 
                               tierhaltung=tierhaltung, adresse=adresse, 
                               kontakte=kontakte, datum=datum, page_title="Behandlungsverlauf")


@bp.route('/<int:behandlungsverlauf_id>/edit_behandlungsverlauf', methods=('GET', 'POST'))
@login_required
def edit_behandlungsverlauf(behandlungsverlauf_id):
    behandlungsverlauf = db.session.query(Behandlungsverlauf).get(behandlungsverlauf_id)
    tierhaltung = db.session.query(Tierhaltung, Person, Tier) \
        .join(Person, Tierhaltung.person_id == Person.id) \
        .join(Tier, Tierhaltung.tier_id == Tier.id).filter(Tierhaltung.person_id==behandlungsverlauf.person_id, Tierhaltung.tier_id==behandlungsverlauf.tier_id).first()
    adresse = db.session.query(Adresse).filter(Adresse.person_id==tierhaltung.Person.id).first()
    kontakte = db.session.query(Kontakt).filter(Kontakt.person_id==tierhaltung.Person.id).all()

    if(request.method == 'POST'):
        behandlungsverlauf, error = fill_and_validate_behandlungsverlauf(behandlungsverlauf, request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, 
                                    tierhaltung=tierhaltung, adresse=adresse, 
                                    kontakte=kontakte, page_title="Behandlungsverlauf")

        db.session.commit()
        path_and_filename = dl_behandlungsverlauf(behandlungsverlauf_id)
        return send_file(path_and_filename, as_attachment=True)
    else:
        return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, 
                                tierhaltung=tierhaltung, adresse=adresse, 
                                kontakte=kontakte, page_title="Behandlungsverlauf")


@bp.route('/<int:behandlungsverlauf_id>/delete_behandlungsverlauf', methods=('GET',))
@login_required
def delete_behandlungsverlauf(behandlungsverlauf_id):
    behandlungsverlauf = db.session.query(Behandlungsverlauf).get(behandlungsverlauf_id)
    db.session.delete(behandlungsverlauf)
    db.session.commit()
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

    if(rechnungsjahr):
        rechnungen = db.session.query(Rechnung, Person, Tier) \
            .join(Person, Rechnung.person_id == Person.id) \
            .join(Tier, Rechnung.tier_id == Tier.id).filter(Rechnung.rechnungsjahr==rechnungsjahr).all()
    else:
        rechnungen = db.session.query(Rechnung, Person, Tier) \
            .join(Person, Rechnung.person_id == Person.id) \
            .join(Tier, Rechnung.tier_id == Tier.id).all()
        
    if(rechnungsjahr):
        str_rechnungsjahr = str(rechnungsjahr)
    else:
        str_rechnungsjahr = ""
    return render_template('ordi/rechnungen.html', rechnungen=rechnungen, rechnungsjahr=str_rechnungsjahr, page_title="Rechnungen")


def dl_rechnung(rechnung_id):
    rechnung = db.session.query(Rechnung).get(rechnung_id)
    rechnungszeilen = db.session.query(Rechnungszeile).filter(Rechnungszeile.rechnung_id==rechnung_id).all()
    tierhaltung = db.session.query(Tierhaltung, Person, Tier) \
        .join(Person, Tierhaltung.person_id == Person.id) \
        .join(Tier, Tierhaltung.tier_id == Tier.id).filter(Tierhaltung.person_id==rechnung.person_id, Tierhaltung.tier_id==rechnung.tier_id, ).first()
    adresse = db.session.query(Adresse).filter(Adresse.person_id==tierhaltung.Person.id).first()

    html = render_template('ordi/prints/print_rechnung.html', rechnung=rechnung, tierhaltung=tierhaltung, adresse=adresse)
    filename = str(rechnung.id) + "_rechnung_fuer_" + tierhaltung.Person.familienname + "_" + tierhaltung.Person.vorname + ".pdf"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
    html2pdf(html, path_and_filename)
    return path_and_filename

@bp.route('/<int:id>/create_rechnung', methods=('GET', 'POST'))
@login_required
def create_rechnung(id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])

    tierhaltung = db.session.query(Tierhaltung, Person, Tier) \
        .join(Person, Tierhaltung.person_id == Person.id) \
        .join(Tier, Tierhaltung.tier_id == Tier.id).filter(Tierhaltung.id==id).first()
    adresse = db.session.query(Adresse).filter(Adresse.person_id==tierhaltung.Person.id).first()
    kontakte = db.session.query(Kontakt).filter(Kontakt.person_id==tierhaltung.Person.id).all()

    if(request.method == 'POST'):
        crechnung, error = fill_and_validate_rechnung(request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        crechnung.rechnungszeilen, zeilen_error = fill_and_validate_rechnungszeilen(req_rechnungszeilen)
        if(len(error) > 0 or len(zeilen_error) > 0):
            flash(error + zeilen_error)
            return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=req_rechnungszeilen, 
                                   artikelwerte=artikelwerte, id=id, tierhaltung=tierhaltung, adresse=adresse, 
                                   kontakte=kontakte, page_title="Rechnung")

        flag, error = crechnung.calc()
        if(flag == False):
            flash(error)
            return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=req_rechnungszeilen, 
                                   artikelwerte=artikelwerte, id=id, tierhaltung=tierhaltung, adresse=adresse, 
                                   kontakte=kontakte, page_title="Rechnung")

        crechnung.person_id = tierhaltung.Person.id
        crechnung.tier_id = tierhaltung.Tier.id
        write_rechnung(crechnung)

        for crechnungszeile in crechnung.rechnungszeilen:
            crechnungszeile.rechnung_id = crechnung.id
            write_rechnungszeile(crechnungszeile)

        return redirect(url_for('ordi.edit_rechnung', rechnung_id=crechnung.id))
    else:
        datum = date.today().strftime("%Y-%m-%d")
        ort = "Wien"
        return render_template('ordi/rechnung.html', rechnung=None, rechnungszeilen=None, datum=datum, ort=ort, 
                               artikelwerte=artikelwerte, id=id, tierhaltung=tierhaltung, adresse=adresse, 
                               kontakte=kontakte, page_title="Rechnung")


@bp.route('/<int:rechnung_id>/edit_rechnung', methods=('GET', 'POST'))
@login_required
def edit_rechnung(rechnung_id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])

    rechnung = db.session.query(Rechnung).get(rechnung_id)
    tierhaltung = db.session.query(Tierhaltung, Person, Tier) \
        .join(Person, Tierhaltung.person_id == Person.id) \
        .join(Tier, Tierhaltung.tier_id == Tier.id).filter(Tierhaltung.person_id==rechnung.person_id, Tierhaltung.tier_id==rechnung.tier_id).first()
    adresse = db.session.query(Adresse).filter(Adresse.person_id==tierhaltung.Person.id).first()
    kontakte = db.session.query(Kontakt).filter(Kontakt.person_id==tierhaltung.Person.id).all()

    if(request.method == 'POST'):
        crechnung, error = fill_and_validate_rechnung(request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        crechnung.rechnungszeilen, zeilen_error = fill_and_validate_rechnungszeilen(req_rechnungszeilen)
        if(len(error) > 0 or len(zeilen_error) > 0):
            flash(error + zeilen_error)
            return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=req_rechnungszeilen, 
                                   artikelwerte=artikelwerte, id=tierhaltung.id, tierhaltung=tierhaltung, adresse=adresse, 
                                   kontakte=kontakte, page_title="Rechnung")

        flag, error = crechnung.calc()
        if(flag == False):
            flash(error)
            return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=req_rechnungszeilen, 
                                   artikelwerte=artikelwerte, id=tierhaltung.id, tierhaltung=tierhaltung, adresse=adresse, 
                                   kontakte=kontakte, page_title="Rechnung")

        update_rechnung(crechnung)
        for crechnungszeile in crechnung.rechnungszeilen:
            if(crechnungszeile.id):
                update_rechnungszeile(crechnungszeile)
            else:
                crechnungszeile.rechnung_id = rechnung_id
                write_rechnungszeile(crechnungszeile)

        path_and_filename = dl_rechnung(crechnung.id)
        return send_file(path_and_filename, as_attachment=True)
    else:
        crechnung = read_rechnung(rechnung_id)
        crechnung.rechnungszeilen = read_rechnungszeilen_for_rechnung(rechnung_id)
        return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=crechnung.rechnungszeilen, 
                               artikelwerte=artikelwerte, id=tierhaltung.id, tierhaltung=tierhaltung, adresse=adresse, 
                               kontakte=kontakte, page_title="Rechnung")


@bp.route('/<int:rechnung_id>/delete_rechnung', methods=('GET',))
@login_required
def delete_rechnung(rechnung_id):
    rechnung = db.session.query(Rechnung).get(rechnung_id)
    db.session.delete(rechnung)
    db.session.commit()
    return redirect(url_for('ordi.rechnungen'))


@bp.route('/<int:rechnungszeile_id>/delete_rechnungszeile', methods=('GET',))
@login_required
def delete_rechnungszeile(rechnungszeile_id):
    rechnungszeile = db.session.query(Rechnungszeile).get(rechnungszeile_id)
    db.session.delete(rechnungszeile)
    db.session.commit()
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
