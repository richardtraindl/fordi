

from datetime import date
import re, os

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, send_file
from werkzeug.exceptions import abort

from ordi.auth import login_required
from ordi.db import get_db
from ordi.dbaccess import *
from ordi.reqhelper import *
from ordi.values import *
from ordi.createpdf import *

bp = Blueprint('ordi', __name__)


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
            kunde = 1
        else:
            kunde = 0
        if(request.form.get('patient')):
            patient = 1
        else:
            patient = 0
    tierhaltungen = read_tierhaltungen(familienname, tiername, kunde, patient)
    return render_template('ordi/tierhaltungen.html', familienname=familienname, tiername=tiername, kunde=kunde, patient=patient, tierhaltungen=tierhaltungen, page_title="Karteikarten")


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


@bp.route('/create_tierhaltung', methods=('GET', 'POST'))
@login_required
def create_tierhaltung():
    if(request.method == 'POST'):
        person, error = fill_and_validate_person(request)
        if(person == None):
            flash(error)
            return render_template('ordi/create_tierhaltung.html')

        tier, error = fill_and_validate_tier(request)
        if(tier == None):
            flash(error)
            return render_template('ordi/create_tierhaltung.html')

        person_id = write_person(person.anredecode, person.titel, person.familienname, person.vorname, person.notiz, person.kunde)
        tier_id = write_tier(tier.tiername, tier.tierart, tier.rasse, tier.farbe, tier.viren, tier.merkmal, tier.geburtsdatum, tier.geschlechtscode, tier.chip_nummer, tier.eu_passnummer, tier.patient)

        adresse = fill_and_validate_adresse(request)[0]
        if(len(adresse.strasse) > 0 or len(adresse.postleitzahl) > 0 or len(adresse.ort) > 0):
            write_adresse(person_id, adresse.strasse, adresse.postleitzahl, adresse.ort)

        kontakte = fill_and_validate_kontakte(request)[0]
        for kontakt in kontakte:
            if(len(kontakt.kontakt) > 0):
                write_kontakt(person_id, kontakt.kontaktcode, kontakt.kontakt, kontakt.kontakt_intern)

        id = write_tierhaltung(person_id, tier_id)
        return redirect(url_for('ordi.show_tierhaltung', id=id))

    anredewerte = []
    for key, value in ANREDE.items():
        anredewerte.append([key, value])

    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])
    return render_template('ordi/create_tierhaltung.html', anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, new="true", page_title="Neue Karteikarte")


@bp.route('/<int:id>/show_tierhaltung', methods=('GET',))
@login_required
def show_tierhaltung(id):
    tierhaltung = read_tierhaltung(id)

    adresse = read_adresse(tierhaltung['person_id'])

    kontakte = read_kontakte(tierhaltung['person_id'])

    behandlungen = []
    tmpbehandlungen = read_behandlungen(id)
    for tmpbehandlung in tmpbehandlungen:
        tmpimpfungen = read_impfungen(tmpbehandlung['id'])
        behandlungen.append([tmpbehandlung, tmpimpfungen])

    behandlungsdatum = date.today().strftime("%Y-%m-%d")

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
    return render_template('ordi/tierhaltung.html', tierhaltung=tierhaltung, anredewerte=anredewerte,  geschlechtswerte=geschlechtswerte, adresse=adresse, kontakte=kontakte, behandlungen=behandlungen, behandlungsdatum=behandlungsdatum, laboreferenzen=laboreferenzen, impfungswerte=impfungswerte, page_title="Karteikarte")


@bp.route('/<int:id>/create_tier', methods=('GET', 'POST'))
@login_required
def create_tier(id):
    if(request.method == 'POST'):
        tier, error = fill_and_validate_tier(request)
        if(tier == None):
            flash(error)
            return render_template('ordi/create_tier.html', id=id)
        tier_id = write_tier(tier.tiername, tier.tierart, tier.rasse, tier.farbe, tier.viren, tier.merkmal, tier.geburtsdatum, tier.geschlechtscode, tier.chip_nummer, tier.eu_passnummer, tier.patient)
        tierhaltung = read_tierhaltung(id)
        newid =  write_tierhaltung(tierhaltung['person_id'], tier_id)
        return redirect(url_for('ordi.show_tierhaltung', id=newid))

    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])
    return render_template('ordi/create_tier.html', geschlechtswerte=geschlechtswerte, new="true", page_title="Neues Tier")


@bp.route('/<int:id>/<int:tier_id>/edit_tier', methods=('GET', 'POST'))
@login_required
def edit_tier(id, tier_id):
    if(request.method == 'POST'):
        tier, error = fill_and_validate_tier(request)
        if(tier == None):
            flash(error)
            return render_template('ordi/edit_tier.html', id=id, tier_id=tier_id)
        update_tier(tier.id, tier.tiername, tier.tierart, tier.rasse, tier.farbe, tier.viren, tier.merkmal, tier.geburtsdatum, tier.geschlechtscode, tier.chip_nummer, tier.eu_passnummer, tier.patient)
        return redirect(url_for('ordi.show_tierhaltung', id=id))

    tierhaltung = read_tierhaltung(id)
    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])
    return render_template('ordi/edit_tier.html', tierhaltung=tierhaltung, geschlechtswerte=geschlechtswerte, page_title="Tier ändern")


@bp.route('/<int:id>/<int:person_id>/edit_person', methods=('GET', 'POST'))
@login_required
def edit_person(id, person_id):
    if(request.method == 'POST'):
        person, error = fill_and_validate_person(request)
        if(person == None):
            flash(error)
            return render_template('ordi/edit_person.html', id=id, person_id=person_id)
        update_person(person.id, person.anredecode, person.titel, person.familienname, person.vorname, person.notiz, person.kunde)

        adresse = fill_and_validate_adresse(request)[0]
        if(len(adresse.strasse) > 0 or len(adresse.postleitzahl) > 0 or len(adresse.ort) > 0):
            if(adresse.id):
                update_adresse(adresse.id, adresse.strasse, adresse.postleitzahl, adresse.ort)
            else:
                write_adresse(adresse.person_id, adresse.strasse, adresse.postleitzahl, adresse.ort)
        else:
            if(adresse.id):
                delete_db_adresse(adresse.id)

        kontakte = fill_and_validate_kontakte(request)[0]
        for kontakt in kontakte:
            if(len(kontakt.kontakt) > 0):
                if(kontakt.id):
                    update_kontakt(kontakt.id, kontakt.kontaktcode, kontakt.kontakt, kontakt.kontakt_intern)
                else:
                    write_kontakt(kontakt.person_id, kontakt.kontaktcode, kontakt.kontakt, kontakt.kontakt_intern)
            else:
                if(kontakt.id):
                    delete_db_kontakt(kontakt.id)
        return redirect(url_for('ordi.show_tierhaltung', id=id))

    tierhaltung = read_tierhaltung(id)
    adresse = read_adresse(person_id)
    kontakte = read_kontakte(person_id)
    anredewerte = []
    for key, value in ANREDE.items():
        anredewerte.append([key, value])
    return render_template('ordi/edit_person.html', tierhaltung=tierhaltung, anredewerte=anredewerte, adresse=adresse, kontakte=kontakte, page_title="Person ändern")


@bp.route('/<int:id>/create_behandlung', methods=('GET', 'POST'))
@login_required
def create_behandlung(id):
    if(request.method == 'POST'):
        behandlung, error = fill_and_validate_behandlung(request)

        if(len(behandlung.gewicht) == 0 and len(behandlung.diagnose) == 0 and len(behandlung.laborwerte1) == 0 and
           len(behandlung.laborwerte2) == 0 and len(behandlung.arzneien) == 0 and len(behandlung.arzneimittel) == 0 and
           len(behandlung.impfungen_extern) == 0):
            return redirect(url_for('ordi.show_tierhaltung', id=id))

        flag, error = behandlung.validate()
        if(flag = False):
            flash(error)
            tierhaltung = read_tierhaltung(id)
            adresse = read_adresse(tierhaltung['person_id'])
            kontakte = read_kontakte(tierhaltung['person_id'])
            behandlungen = read_behandlungen(id)
            return render_template('ordi/show_tierhaltung.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, behandlungen=behandlungen)

        tierhaltung = read_tierhaltung(id)
        behandlung_id = write_behandlung(tierhaltung['tier_id'], behandlung.behandlungsdatum, behandlung.gewicht, behandlung.diagnose, behandlung.laborwerte1, behandlung.laborwerte2, behandlung.arzneien, behandlung.arzneimittel, behandlung.impfungen_extern)
        if(len(impfungen_extern) > 0):
            impfungstexte = impfungen_extern.split(', ')
        else:
            impfungstexte = []
        save_or_delete_impfungen(behandlung_id, impfungstexte)
    return redirect(url_for('ordi.show_tierhaltung', id=id))


def build_behandlungen(data):
    behandlungen = []
    for idx in range(len(data[0])):
        behandlung = []
        for row in data:
            behandlung.append(row[idx])
        behandlungen.append(behandlung)
    return behandlungen

@bp.route('/<int:id>/save_behandlungen', methods=('GET', 'POST'))
@login_required
def save_behandlungen(id):
    if(request.method == 'POST'):
        req_behandlungen = build_behandlungen(request)
        behandlungen, error = fill_and_validate_behandlungen(req_behandlungen):
        if(behandlungen == None):
            flash(error)
            tierhaltung = read_tierhaltung(id)
            adresse = read_adresse(tierhaltung['person_id'])
            kontakte = read_kontakte(tierhaltung['person_id'])
            return render_template('ordi/show_tierhaltung.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, req_behandlungen=req_behandlungen)

        tierhaltung = read_tierhaltung(id)
        for behandlung in behandlungen:
            if(len(behandlung_id) == 0):
                behandlung_id = write_behandlung(tierhaltung['tier_id'], behandlung.behandlungsdatum, behandlung.gewicht, behandlung.diagnose, behandlung.laborwerte1, behandlung.laborwerte2, behandlung.arzneien, behandlung.arzneimittel, behandlung.impfungen_extern)
            else:
                update_behandlung(behandlung_id, behandlung.behandlungsdatum, behandlung.gewicht, behandlung.diagnose, behandlung.laborwerte1, behandlung.laborwerte2, behandlung.arzneien, behandlung.arzneimittel, behandlung.impfungen_extern)
            if(len(behandlung.impfungen_extern) > 0):
                impfungstexte = behandlung.impfungen_extern.split(',')
            else:
                impfungstexte = []
            save_or_delete_impfungen(behandlung_id, impfungstexte)
    return redirect(url_for('ordi.show_tierhaltung', id=id))


@bp.route('/<int:id>/create_behandlungsverlauf', methods=('GET', 'POST'))
@login_required
def create_behandlungsverlauf(id):
    if(request.method == 'POST'):
        datum = request.form['datum']
        if(len(datum) == 0):
            datum = date.today().strftime("%Y-%m-%d")
        diagnose = request.form['diagnose']
        behandlung = request.form['behandlung']
        tierhaltung = read_tierhaltung(id)
        adresse = read_adresse(tierhaltung['person_id'])
        behandlungsverlauf_id = write_behandlungsverlauf(tierhaltung['person_id'], tierhaltung['tier_id'], datum, diagnose, behandlung)
        behandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
        html = render_template('ordi/prints/print_behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, tierhaltung=tierhaltung, adresse=adresse)
        filename = str(behandlungsverlauf['id']) + "_behandlungsverlauf_fuer_" + tierhaltung['familienname'] + "_" + tierhaltung['vorname'] + ".pdf"
        path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
        html2pdf(html, path_and_filename)
        return send_file(path_and_filename, as_attachment=True)
    else:
        tierhaltung = read_tierhaltung(id)
        adresse = read_adresse(tierhaltung['person_id'])
        kontakte = read_kontakte(tierhaltung['person_id'])
        return render_template('ordi/behandlungsverlauf.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, page_title="Behandlungsverlauf")


@bp.route('/<int:behandlungsverlauf_id>/edit_behandlungsverlauf', methods=('GET', 'POST'))
@login_required
def edit_behandlungsverlauf(behandlungsverlauf_id):
    if(request.method == 'POST'):
        datum = request.form['datum']
        if(len(datum) == 0):
            datum = date.today().strftime("%Y-%m-%d")
        diagnose = request.form['diagnose']
        behandlung = request.form['behandlung']
        update_behandlungsverlauf(behandlungsverlauf_id, datum, diagnose, behandlung)
        behandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
        tierhaltung = read_tierhaltung_by_children(behandlungsverlauf['person_id'], behandlungsverlauf['tier_id'])
        adresse = read_adresse(behandlungsverlauf['person_id'])
        html = render_template('ordi/prints/print_behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, tierhaltung=tierhaltung, adresse=adresse)
        filename = str(behandlungsverlauf['id']) + "_behandlungsverlauf_fuer_" + tierhaltung['familienname'] + "_" + tierhaltung['vorname'] + ".pdf"
        path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
        html2pdf(html, path_and_filename)
        return send_file(path_and_filename, as_attachment=True)
    behandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
    tierhaltung = read_tierhaltung_by_children(behandlungsverlauf['person_id'], behandlungsverlauf['tier_id'])
    adresse = read_adresse(behandlungsverlauf['person_id'])
    kontakte = read_kontakte(behandlungsverlauf['person_id'])
    return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, page_title="Behandlungsverlauf")


@bp.route('/<int:id>/create_rechnung', methods=('GET', 'POST'))
@login_required
def create_rechnung(id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])

    tierhaltung = read_tierhaltung(id)
    adresse = read_adresse(tierhaltung['person_id'])
    kontakte = read_kontakte(tierhaltung['person_id'])
        
    if(request.method == 'POST'):
        rechnung, error = fill_and_validate_rechnung(request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        rechnungszeilen, zeilen_error = fill_and_validate_rechnungszeilen(req_rechnungszeilen)
        if(rechnung == None or rechnungszeilen == None):
            flash(error + zeilen_error)
            return render_template('ordi/rechnung.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, req_rechnungszeilen=req_rechnungszeilen, artikelwerte=artikelwerte, page_title="Rechnung")

        flag, error = rechnung.calc(rechnungszeilen)
        if(flag == False):
            flash(error)
            return render_template('ordi/rechnung.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, req_rechnungszeilen=req_rechnungszeilen, artikelwerte=artikelwerte, page_title="Rechnung")

        rechnung_id = write_rechnung(tierhaltung['person_id'], tierhaltung['tier_id'], rechnung.rechnungsjahr, rechnung.rechnungslfnr, rechnung.ausstellungsdatum, rechnung.ausstellungsort, rechnung.diagnose, rechnung.bezahlung, calc.brutto_summe, calc.netto_summe, calc.steuerbetrag_zwanzig, calc.steuerbetrag_dreizehn, calc.steuerbetrag_zehn)
        for rechnungszeile in rechnungszeilen:
            if(rechnungszeile.id):
                update_rechnungszeile(rechnungszeile.id, rechnungszeile.datum, rechnungszeile.artikelcode, rechnungszeile.artikel, rechnungszeile.betrag)
            else:
                write_rechnungszeile(rechnung_id, rechnungszeile.datum, rechnungszeile.artikelcode, rechnungszeile.artikel, rechnungszeile.betrag)                

        rechnung = read_rechnung(rechnung_id)
        rechnungszeilen = read_rechnungszeilen(rechnung_id)
        html = render_template('ordi/prints/print_rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen, tierhaltung=tierhaltung, adresse=adresse)
        filename = str(rechnung['id']) + "_rechnung_fuer_" + tierhaltung['familienname'] + "_" + tierhaltung['vorname'] + ".pdf"
        path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
        html2pdf(html, path_and_filename)
        return send_file(path_and_filename, as_attachment=True)
        #return redirect(url_for('ordi.edit_rechnung', rechnung_id=rechnung_id))

    rechnungszeile_datum = date.today().strftime("%Y-%m-%d")
    ausstellungsdatum = date.today().strftime("%Y-%m-%d")
    ausstellungsort = "Wien"
    return render_template('ordi/rechnung.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, ausstellungsdatum=ausstellungsdatum, ausstellungsort=ausstellungsort, rechnungszeile_datum=rechnungszeile_datum, artikelwerte=artikelwerte, page_title="Rechnung")


@bp.route('/<int:rechnung_id>/edit_rechnung', methods=('GET', 'POST'))
@login_required
def edit_rechnung(rechnung_id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])

    rechnung = read_rechnung(rechnung_id)
    tierhaltung = read_tierhaltung_by_children(rechnung['person_id'], rechnung['tier_id'])
    adresse = read_adresse(rechnung['person_id'])
    kontakte = read_kontakte(rechnung['person_id'])

    if(request.method == 'POST'):
        rechnung, error = fill_and_validate_rechnung(request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        rechnungszeilen, zeilen_error = fill_and_validate_rechnungszeilen(req_rechnungszeilen)
        if(rechnung == None or rechnungszeilen == None):
            flash(error + zeilen_error)
            return render_template('ordi/rechnung.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, req_rechnungszeilen=req_rechnungszeilen, artikelwerte=artikelwerte, page_title="Rechnung")

        flag, error = rechnung.calc(rechnungszeilen)
        if(flag == False):
            flash(error)
            return render_template('ordi/rechnung.html', rechnung_id=rechnung_id, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, req_rechnungszeilen=req_rechnungszeilen, artikelwerte=artikelwerte, page_title="Rechnung")
        else:
            update_rechnung(rechnung_id, rechnung.rechnungsjahr, rechnung.rechnungslfnr, rechnung.ausstellungsdatum, rechnung.ausstellungsort, rechnung.diagnose, rechnung.bezahlung, calc.brutto_summe, calc.netto_summe, calc.steuerbetrag_zwanzig, calc.steuerbetrag_dreizehn, calc.steuerbetrag_zehn)

        for rechnungszeile in rechnungszeilen:
            if(rechnungszeile.id):
                update_rechnungszeile(rechnungszeile.id, rechnungszeile.datum, rechnungszeile.artikelcode, rechnungszeile.artikel, rechnungszeile.betrag)                
            else:
                write_rechnungszeile(rechnung_id, rechnungszeile.datum, rechnungszeile.artikelcode, rechnungszeile.artikel, rechnungszeile.betrag)

        rechnung = read_rechnung(rechnung_id)
        rechnungszeilen = read_rechnungszeilen(rechnung_id)
        html = render_template('ordi/prints/print_rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen, tierhaltung=tierhaltung, adresse=adresse)
        filename = str(rechnung['id']) + "_rechnung_fuer_" + tierhaltung['familienname'] + "_" + tierhaltung['vorname'] + ".pdf"
        path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
        html2pdf(html, path_and_filename)
        return send_file(path_and_filename, as_attachment=True)
        #return redirect(url_for('ordi.edit_rechnung', rechnung_id=rechnung_id))

    rechnung = read_rechnung(rechnung_id)
    rechnungszeilen = read_rechnungszeilen(rechnung_id)
    rechnungszeile_datum = date.today().strftime("%Y-%m-%d")
    return render_template('ordi/rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen, rechnungszeile_datum=rechnungszeile_datum, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, artikelwerte=artikelwerte, page_title="Rechnung")


@bp.route('/<int:rechnung_id>/print_rechnung', methods=('GET',))
@login_required
def print_rechnung(rechnung_id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])
    rechnung = read_rechnung(rechnung_id)
    rechnungszeilen = read_rechnungszeilen(rechnung_id)
    tierhaltung = read_tierhaltung_by_children(rechnung['person_id'], rechnung['tier_id'])
    adresse = read_adresse(tierhaltung['person_id'])
    html = render_template('ordi/prints/print_rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen, tierhaltung=tierhaltung, adresse=adresse)
    filename = str(rechnung['id']) + "_rechnung_fuer_" + tierhaltung['familienname'] + "_" + tierhaltung['vorname'] + ".pdf"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
    html2pdf(html, path_and_filename)
    return send_file(path_and_filename, as_attachment=True)


@bp.route('/<int:id>/<int:behandlung_id>/delete_behandlung', methods=('GET',))
@login_required
def delete_behandlung(id, behandlung_id):
    delete_db_behandlung(behandlung_id)
    return redirect(url_for('ordi.show_tierhaltung', id=id))


@bp.route('/<int:behandlungsverlauf_id>/delete_behandlungsverlauf', methods=('GET',))
@login_required
def delete_behandlungsverlauf(behandlungsverlauf_id):
    delete_db_behandlungsverlauf(behandlungsverlauf_id)
    return redirect(url_for('ordi.behandlungsverlaeufe'))


@bp.route('/<int:rechnung_id>/delete_rechnung', methods=('GET',))
@login_required
def delete_rechnung(rechnung_id):
    delete_db_rechnung(rechnung_id)
    return redirect(url_for('ordi.rechnungen'))


@bp.route('/<int:rechnungszeile_id>/delete_rechnungszeile', methods=('GET',))
@login_required
def delete_rechnungszeile(rechnungszeile_id):
    rechnungszeile = read_rechnungszeile(rechnungszeile_id)
    delete_db_rechnungszeile(rechnungszeile_id)
    return redirect(url_for('ordi.edit_rechnung', rechnung_id=rechnungszeile['rechnung_id']))


@bp.route('/<int:id>/delete_tierhaltung', methods=('GET',))
@login_required
def delete_tierhaltung(id):
    delete_db_tierhaltung(id)
    return redirect(url_for('ordi.index'))

