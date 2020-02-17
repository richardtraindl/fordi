

from datetime import date
from operator import attrgetter
import re, os

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, send_file
from werkzeug.exceptions import abort

from . import db
from ordi.auth import login_required
from ordi.models import *
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
                Person.kunde==kunde, Tier.patient==patient).all()

    return render_template('ordi/tierhaltungen.html', tierhaltungen=tierhaltungen, 
        familienname=familienname, tiername=tiername, kunde=kunde, patient=patient, 
        page_title="Karteikarten")


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
            tier = Tier()
            return render_template('ordi/create_tierhaltung.html', 
                person=person, tier=tier, anredewerte=anredewerte, 
                geschlechtswerte=geschlechtswerte, page_title="Neue Karteikarte")

        tier, error = fill_and_validate_tier(None, request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/create_tierhaltung.html', 
                person=person, tier=tier, anredewerte=anredewerte, 
                geschlechtswerte=geschlechtswerte, page_title="Neue Karteikarte")

        db.session.add(person)
        db.session.add(tier)
        db.session.commit()

        adresse = fill_and_validate_adresse(None, request)[0]
        if(len(adresse.strasse) > 0 or len(adresse.postleitzahl) > 0 or len(adresse.ort) > 0):
            adresse.person_id=person.id
            db.session.add(adresse)
            db.session.commit()

        req_kontakte = build_kontakte(request)
        kontakte = fill_and_validate_kontakte(req_kontakte, request)[0]
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
        person = Person()
        person.kontakte.append(Kontakt(kontaktcode=KONTAKT['Telefon']))
        person.kontakte.append(Kontakt(kontaktcode=KONTAKT['Telefon']))
        person.kontakte.append(Kontakt(kontaktcode=KONTAKT['E-Mail']))
        person.kontakte.append(Kontakt(kontaktcode=KONTAKT['E-Mail']))
        tier = Tier()
        return render_template('ordi/create_tierhaltung.html', person=person, 
            tier=tier, anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, 
            page_title="Neue Karteikarte")


@bp.route('/<int:id>/show_tierhaltung', methods=('GET',))
@login_required
def show_tierhaltung(id):
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
    behandlungen = db.session.query(Behandlung).filter(Behandlung.tier_id == tierhaltung.tier.id).order_by(Behandlung.behandlungsdatum.asc()).all()
    datum = datetime.today().strftime("%Y-%m-%d")

    return render_template('ordi/tierhaltung.html', tierhaltung=tierhaltung, 
        behandlungen=behandlungen, datum=datum, anredewerte=anredewerte, 
        geschlechtswerte=geschlechtswerte, laborreferenzen=laborreferenzen, 
        impfungswerte=impfungswerte, page_title="Karteikarte")


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
    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])

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
    else:
        tier = Tier()
        return render_template('ordi/create_tier.html', tier=tier, geschlechtswerte=geschlechtswerte, 
            page_title="Neues Tier")


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
            return render_template('ordi/edit_tier.html', id=id, tier=tier, 
                geschlechtswerte=geschlechtswerte, page_title="Tier ändern")
        else:
            db.session.commit()
            return redirect(url_for('ordi.show_tierhaltung', id=id))
    else:
        tier = db.session.query(Tier).get(tier_id)
        return render_template('ordi/edit_tier.html', id=id, tier=tier, 
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
            return render_template('ordi/edit_person.html', id=id, person=person, 
                anredewerte=anredewerte, page_title="Person ändern")

        db.session.commit()

        adresse = fill_and_validate_adresse(person.adresse, request)[0]
        if(len(adresse.strasse) > 0 or len(adresse.postleitzahl) > 0 or len(adresse.ort) > 0):
            if(adresse.id == None):
                adresse.person_id=person_id
                db.session.add(adresse)
                db.session.commit()
        else:
            if(adresse.id):
                db.session.delete(adresse)
                db.session.commit()

        req_kontakte = build_kontakte(request)
        kontakte = fill_and_validate_kontakte(req_kontakte, request)[0]
        for kontakt in kontakte:
            if(len(kontakt.kontakt) > 0):
                if(kontakt.id == None):
                    #kontakt.person_id=person_id
                    db.session.add(kontakt)
                db.session.commit()
            else:
                if(kontakt.id):
                    kontakt = db.session.query(Kontakt).get(kontakt.id)
                    db.session.delete(kontakt)
                    db.session.commit()

        return redirect(url_for('ordi.show_tierhaltung', id=id))

    person = db.session.query(Person).get(person_id)
    telcnt = 0
    mailcnt = 0
    for kontakt in person.kontakte:
        if(kontakt.kontaktcode == 1):
            telcnt += 1
        elif(kontakt.kontaktcode == 3):
            mailcnt += 1
    if(telcnt < 2):
        for i in range(2 - telcnt):
            person.kontakte.append(Kontakt(kontaktcode=1))
    if(mailcnt < 2):
        for i in range(2 - mailcnt):
            person.kontakte.append(Kontakt(kontaktcode=3))
    person.kontakte.sort(key=attrgetter('kontaktcode'))

    return render_template('ordi/edit_person.html', id=id, person=person, 
        anredewerte=anredewerte, page_title="Person ändern")
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

    return render_template('ordi/behandlungsverlaeufe.html', behandlungsverlaeufe=behandlungsverlaeufe, 
        behandlungsjahr=str_behandlungsjahr, page_title="Behandlungsverläufe")


def dl_behandlungsverlauf(behandlungsverlauf_id):
    behandlungsverlauf = db.session.query(Behandlungsverlauf).get(behandlungsverlauf_id)

    html = render_template('ordi/prints/print_behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf)

    filename = str(behandlungsverlauf.id) + "_behandlungsverlauf_fuer_" + behandlungsverlauf.person.familienname + \
        "_" + behandlungsverlauf.person.vorname + ".pdf"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)

    html2pdf(html, path_and_filename)

    return path_and_filename

@bp.route('/<int:id>/create_behandlungsverlauf', methods=('GET', 'POST'))
@login_required
def create_behandlungsverlauf(id):
    tierhaltung = db.session.query(Tierhaltung).get(id)

    if(request.method == 'POST'):
        behandlungsverlauf, error = fill_and_validate_behandlungsverlauf(None, request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/behandlungsverlauf.html', id=id, 
                behandlungsverlauf=behandlungsverlauf, 
                datum=datum, page_title="Behandlungsverlauf")

        behandlungsverlauf.person_id = tierhaltung.person.id
        behandlungsverlauf.tier_id = tierhaltung.tier.id
        db.session.add(behandlungsverlauf)
        db.session.commit()
        return redirect(url_for('ordi.edit_behandlungsverlauf', behandlungsverlauf_id=behandlungsverlauf.id))
    else:
        datum = date.today().strftime("%Y-%m-%d")
        return render_template('ordi/behandlungsverlauf.html', id=id, 
            person = tierhaltung.person, tier = tierhaltung.tier, 
            behandlungsverlauf=None, datum=datum, page_title="Behandlungsverlauf")


@bp.route('/<int:behandlungsverlauf_id>/edit_behandlungsverlauf', methods=('GET', 'POST'))
@login_required
def edit_behandlungsverlauf(behandlungsverlauf_id):
    behandlungsverlauf = db.session.query(Behandlungsverlauf).get(behandlungsverlauf_id)

    if(request.method == 'POST'):
        behandlungsverlauf, error = fill_and_validate_behandlungsverlauf(behandlungsverlauf, request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, 
                page_title="Behandlungsverlauf")

        db.session.commit()
        path_and_filename = dl_behandlungsverlauf(behandlungsverlauf_id)
        return send_file(path_and_filename, as_attachment=True)
    else:
        return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, 
            page_title="Behandlungsverlauf")


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


def calc_and_fill_rechnung(rechnung, rechnungszeilen):
    rechnung.brutto_summe = 0
    rechnung.steuerbetrag_zwanzig = 0
    rechnung.steuerbetrag_dreizehn = 0
    rechnung.steuerbetrag_zehn = 0

    for rechnungszeile in rechnungszeilen:
        try:
            steuersatz = ARTIKEL_STEUER[rechnungszeile.artikelcode]
        except:
            return "Falsche Artikelart."
        try:
            betrag = round(rechnungszeile.betrag, 2)
        except:
            return "Betrag ist keine Zahl."

        rechnung.brutto_summe += betrag
        nettobetrag = round(betrag * 100 / (100 + steuersatz))
        if(steuersatz == 20):
            rechnung.steuerbetrag_zwanzig += (betrag - nettobetrag)
        elif(steuersatz == 13):
            rechnung.steuerbetrag_dreizehn += (betrag - nettobetrag)
        else: # steuersatz == 10
            rechnung.steuerbetrag_zehn += (betrag - nettobetrag)

    rechnung.netto_summe = rechnung.brutto_summe - (rechnung.steuerbetrag_zwanzig + rechnung.steuerbetrag_dreizehn + rechnung.steuerbetrag_zehn)
    return ""

def dl_rechnung(rechnung_id):
    rechnung = db.session.query(Rechnung).get(rechnung_id)
    rechnungszeilen = db.session.query(Rechnungszeile).filter(Rechnungszeile.rechnung_id==rechnung_id).all()

    html = render_template('ordi/prints/print_rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen)

    filename = str(rechnung.id) + "_rechnung_fuer_" + rechnung.person.familienname + "_" + rechnung.person.vorname + ".pdf"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)

    html2pdf(html, path_and_filename)

    return path_and_filename

@bp.route('/<int:id>/create_rechnung', methods=('GET', 'POST'))
@login_required
def create_rechnung(id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])

    tierhaltung = db.session.query(Tierhaltung).get(id)

    if(request.method == 'POST'):
        rechnung, error = fill_and_validate_rechnung(None, request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        if(len(req_rechnungszeilen) == 0):
            error += "Es muss mind. eine Rechnungszeile vorhanden sein. "
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/rechnung.html', id=id, rechnung=rechnung, 
                rechnungszeilen=req_rechnungszeilen, person = tierhaltung.person, 
                tier = tierhaltung.tier, artikelwerte=artikelwerte, page_title="Rechnung")

        rechnungszeilen = []
        for req_rechnungszeile in req_rechnungszeilen:
            rechnungszeile, error = fill_and_validate_rechnungszeile(None, req_rechnungszeile)
            if(len(error) > 0):
                flash(error)
                return render_template('ordi/rechnung.html', id=id, rechnung=rechnung, 
                    rechnungszeilen=req_rechnungszeilen, person = tierhaltung.person, 
                    tier = tierhaltung.tier, artikelwerte=artikelwerte, page_title="Rechnung")
            else:
                rechnungszeilen.append(rechnungszeile)

        error = calc_and_fill_rechnung(rechnung, rechnungszeilen)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/rechnung.html', id=id, rechnung=rechnung, 
                rechnungszeilen=req_rechnungszeilen, person = tierhaltung.person, 
                tier = tierhaltung.tier, artikelwerte=artikelwerte, page_title="Rechnung")

        rechnung.person_id = tierhaltung.person.id
        rechnung.tier_id = tierhaltung.tier.id
        db.session.add(rechnung)
        db.session.commit()

        for rechnungszeile in rechnungszeilen:
            rechnungszeile.rechnung_id = rechnung.id
            db.session.add(rechnungszeile)
        db.session.commit()
        return redirect(url_for('ordi.edit_rechnung', rechnung_id=rechnung.id))
    else:
        datum = datetime.now().strftime("%Y-%m-%d")
        ort = "Wien"
        return render_template('ordi/rechnung.html', id=id, rechnung=None, 
            rechnungszeilen=None, person = tierhaltung.person, tier = tierhaltung.tier, 
            datum=datum, ort=ort, artikelwerte=artikelwerte, page_title="Rechnung")


@bp.route('/<int:rechnung_id>/edit_rechnung', methods=('GET', 'POST'))
@login_required
def edit_rechnung(rechnung_id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])

    rechnung = db.session.query(Rechnung).get(rechnung_id)
    rechnungszeilen = db.session.query(Rechnungszeile).filter(Rechnungszeile.rechnung_id==rechnung.id).all()

    if(request.method == 'POST'):
        rechnung, error = fill_and_validate_rechnung(rechnung, request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        if(len(req_rechnungszeilen) == 0):
            error += "Es muss mind. eine Rechnungszeile vorhanden sein. "
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/rechnung.html', rechnung=rechnung, rechnungszeilen=req_rechnungszeilen, 
                artikelwerte=artikelwerte, page_title="Rechnung")

        new_rechnungszeilen = []
        for req_rechnungszeile in req_rechnungszeilen:
            new_rechnungszeile = None
            if(len(req_rechnungszeile['rechnungszeile_id']) > 0):
                try:
                    rechnungszeile_id = int(req_rechnungszeile['rechnungszeile_id'])
                    new_rechnungszeile = db.session.query(Rechnungszeile).get(rechnungszeile_id)
                except:
                    rechnungszeile_id = None

            new_rechnungszeile, error = fill_and_validate_rechnungszeile(new_rechnungszeile, req_rechnungszeile)
            if(len(error) > 0):
                flash(error)
                return render_template('ordi/rechnung.html', rechnung=rechnung, rechnungszeilen=req_rechnungszeilen, 
                    artikelwerte=artikelwerte, page_title="Rechnung")
            else:
                new_rechnungszeilen.append(new_rechnungszeile)

        error = calc_and_fill_rechnung(rechnung, new_rechnungszeilen)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/rechnung.html', rechnung=rechnung, rechnungszeilen=req_rechnungszeilen, 
                artikelwerte=artikelwerte, page_title="Rechnung")

        db.session.commit() # commit rechnung

        for new_rechnungszeile in new_rechnungszeilen:
            if(new_rechnungszeile.id == None):
                new_rechnungszeile.rechnung_id = rechnung.id
                db.session.add(new_rechnungszeile)
        db.session.commit()

        for rechnungszeile in rechnungszeilen:
            found = False
            for new_rechnungszeile in new_rechnungszeilen:
                if(rechnungszeile.id == new_rechnungszeile.id):
                    found = True
                    break
            if(found == False):
                db.session.delete(rechnungszeile)
        db.session.commit()

        path_and_filename = dl_rechnung(rechnung.id)
        return send_file(path_and_filename, as_attachment=True)
    else:
        return render_template('ordi/rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen, artikelwerte=artikelwerte, 
            page_title="Rechnung")


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
    return redirect(url_for('ordi.edit_rechnung', rechnung_id=rechnungszeile.rechnung_id))
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
