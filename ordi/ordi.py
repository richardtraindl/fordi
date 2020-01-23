

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
        cperson, error = fill_and_validate_person(request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/create_tierhaltung.html')

        ctier, error = fill_and_validate_tier(request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/create_tierhaltung.html')

        cperson.id = write_person(cperson.anredecode, cperson.titel, cperson.familienname, cperson.vorname, cperson.notiz, cperson.kunde)
        ctier.id = write_tier(ctier.tiername, ctier.tierart, ctier.rasse, ctier.farbe, ctier.viren, ctier.merkmal, ctier.geburtsdatum, ctier.geschlechtscode, ctier.chip_nummer, ctier.eu_passnummer, ctier.patient)

        cadresse = fill_and_validate_adresse(request)[0]
        if(len(cadresse.strasse) > 0 or len(cadresse.postleitzahl) > 0 or len(cadresse.ort) > 0):
            cadresse.id = write_adresse(cperson.id, cadresse.strasse, cadresse.postleitzahl, cadresse.ort)

        ckontakte = fill_and_validate_kontakte(request)[0]
        for ckontakt in ckontakte:
            if(len(ckontakt.kontakt) > 0):
                ckontakt.id = write_kontakt(cperson.id, ckontakt.kontaktcode, ckontakt.kontakt, ckontakt.kontakt_intern)

        id = write_tierhaltung(cperson.id, ctier.id)
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
    
    cperson = read_person(tierhaltung['person_id'])
    cperson.adresse = read_adresse_for_person(cperson.id)
    cperson.kontakte = read_kontakte_for_person(cperson.id)

    ctier = read_tier(tierhaltung['tier_id'])
    cbehandlungen = read_behandlungen_for_tier(ctier.id)

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
    return render_template('ordi/tierhaltung.html', id=id, person=cperson, tier=ctier, behandlungen=cbehandlungen, datum=datum, 
                           anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, laboreferenzen=laboreferenzen, impfungswerte=impfungswerte, page_title="Karteikarte")


@bp.route('/<int:id>/create_tier', methods=('GET', 'POST'))
@login_required
def create_tier(id):
    if(request.method == 'POST'):
        ctier, error = fill_and_validate_tier(request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/create_tier.html', id=id)
        ctier.id = write_tier(ctier.tiername, ctier.tierart, ctier.rasse, ctier.farbe, ctier.viren, ctier.merkmal, ctier.geburtsdatum, ctier.geschlechtscode, ctier.chip_nummer, ctier.eu_passnummer, ctier.patient)
        tierhaltung = read_tierhaltung(id)
        newid =  write_tierhaltung(tierhaltung['person_id'], ctier.id)
        return redirect(url_for('ordi.show_tierhaltung', id=newid))

    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])
    return render_template('ordi/create_tier.html', geschlechtswerte=geschlechtswerte, new="true", page_title="Neues Tier")


@bp.route('/<int:id>/<int:tier_id>/edit_tier', methods=('GET', 'POST'))
@login_required
def edit_tier(id, tier_id):
    if(request.method == 'POST'):
        ctier, error = fill_and_validate_tier(request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/edit_tier.html', id=id, tier_id=tier_id)
        update_tier(tier.id, ctier.tiername, ctier.tierart, ctier.rasse, ctier.farbe, ctier.viren, ctier.merkmal, ctier.geburtsdatum, ctier.geschlechtscode, ctier.chip_nummer, ctier.eu_passnummer, ctier.patient)
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
        cperson, error = fill_and_validate_person(request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/edit_person.html', id=id, person_id=person_id)
        update_person(cperson.id, cperson.anredecode, cperson.titel, cperson.familienname, cperson.vorname, cperson.notiz, cperson.kunde)

        cadresse = fill_and_validate_adresse(request)[0]
        if(len(cadresse.strasse) > 0 or len(cadresse.postleitzahl) > 0 or len(cadresse.ort) > 0):
            if(cadresse.id):
                update_adresse(cadresse.id, cadresse.strasse, cadresse.postleitzahl, cadresse.ort)
            else:
                write_adresse(cadresse.person_id, cadresse.strasse, cadresse.postleitzahl, cadresse.ort)
        else:
            if(cadresse.id):
                delete_db_adresse(cadresse.id)

        ckontakte = fill_and_validate_kontakte(request)[0]
        for ckontakt in ckontakte:
            if(len(ckontakt.kontakt) > 0):
                if(ckontakt.id):
                    update_kontakt(ckontakt.id, ckontakt.kontaktcode, ckontakt.kontakt, ckontakt.kontakt_intern)
                else:
                    write_kontakt(ckontakt.person_id, ckontakt.kontaktcode, ckontakt.kontakt, ckontakt.kontakt_intern)
            else:
                if(ckontakt.id):
                    delete_db_kontakt(ckontakt.id)
        return redirect(url_for('ordi.show_tierhaltung', id=id))

    tierhaltung = read_tierhaltung(id)
    cadresse = read_adresse_for_person(person_id)
    ckontakte = read_kontakte_for_person(person_id)
    anredewerte = []
    for key, value in ANREDE.items():
        anredewerte.append([key, value])
    return render_template('ordi/edit_person.html', tierhaltung=tierhaltung, anredewerte=anredewerte, adresse=cadresse, kontakte=ckontakte, page_title="Person ändern")


@bp.route('/<int:id>/create_behandlung', methods=('GET', 'POST'))
@login_required
def create_behandlung(id):
    if(request.method == 'POST'):
        cbehandlung, error = fill_and_validate_behandlung(request)

        if(cbehandlung.id == None and len(cbehandlung.gewicht) == 0 and len(cbehandlung.diagnose) == 0 and len(cbehandlung.laborwerte1) == 0 and
           len(cbehandlung.laborwerte2) == 0 and len(cbehandlung.arzneien) == 0 and len(cbehandlung.arzneimittel) == 0 and
           len(cbehandlung.impfungen_extern) == 0):
            return redirect(url_for('ordi.show_tierhaltung', id=id))

        if(len(error) > 0):
            flash(error)
            tierhaltung = read_tierhaltung(id)
            adresse = read_adresse(tierhaltung['person_id'])
            kontakte = read_kontakte(tierhaltung['person_id'])
            #behandlungen = read_behandlungen(id)
            return render_template('ordi/tierhaltung.html', id=id, tier=ctier, person=cperson, behandlungen=cbehandlungen)

        #tierhaltung = read_tierhaltung(id)
        behandlung.id = write_behandlung(behandlung.tier_id, behandlung.behandlungsdatum, behandlung.gewicht, behandlung.diagnose, behandlung.laborwerte1, behandlung.laborwerte2, behandlung.arzneien, behandlung.arzneimittel, behandlung.impfungen_extern)
        if(len(impfungen_extern) > 0):
            impfungstexte = impfungen_extern.split(', ')
        else:
            impfungstexte = []
        save_or_delete_impfungen(behandlung.id, impfungstexte)
    return redirect(url_for('ordi.show_tierhaltung', id=id))


@bp.route('/<int:id>/save_behandlungen', methods=('GET', 'POST'))
@login_required
def save_behandlungen(id):
    if(request.method == 'POST'):
        req_behandlungen = build_behandlungen(request)
        cbehandlungen, error = fill_and_validate_behandlungen(req_behandlungen)
        if(len(error) > 0):
            flash(error)
            tierhaltung = read_tierhaltung(id)
            cperson = read_person(tierhaltung['person_id'])
            cperson.adresse = read_adresse(tierhaltung['person_id'])
            cperson.kontakte = read_kontakte(tierhaltung['person_id'])
            ctier = read_tier(tierhaltung['tier_id'])
            return render_template('ordi/tierhaltung.html', id=id, person=cperson, tier=ctier, behandlungen=cbehandlungen)

        tierhaltung = read_tierhaltung(id)
        for behandlung in cbehandlungen:
            if(behandlung.id):
                update_behandlung(behandlung.id, behandlung.behandlungsdatum, behandlung.gewicht, behandlung.diagnose, behandlung.laborwerte1, behandlung.laborwerte2, behandlung.arzneien, behandlung.arzneimittel, behandlung.impfungen_extern)
            else:
                behandlung.id = write_behandlung(tierhaltung['tier_id'], behandlung.behandlungsdatum, behandlung.gewicht, behandlung.diagnose, behandlung.laborwerte1, behandlung.laborwerte2, behandlung.arzneien, behandlung.arzneimittel, behandlung.impfungen_extern)                
            if(len(behandlung.impfungen_extern) > 0):
                impfungstexte = behandlung.impfungen_extern.split(',')
            else:
                impfungstexte = []
            save_or_delete_impfungen(behandlung.id, impfungstexte)
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
        crechnung, error = fill_and_validate_rechnung(request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        crechnungszeilen, zeilen_error = fill_and_validate_rechnungszeilen(req_rechnungszeilen)
        if(len(error) > 0 or len(zeilen_error) > 0):
            flash(error + zeilen_error)
            return render_template('ordi/rechnung.html', rechnung=None, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, rechnungszeilen=req_rechnungszeilen, artikelwerte=artikelwerte, page_title="Rechnung")

        flag, error = crechnung.calc(crechnungszeilen)
        if(flag == False):
            flash(error)
            return render_template('ordi/rechnung.html', rechnung=None, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, rechnungszeilen=req_rechnungszeilen, artikelwerte=artikelwerte, page_title="Rechnung")

        rechnung_id = write_rechnung(tierhaltung['person_id'], tierhaltung['tier_id'], crechnung.rechnungsjahr, crechnung.rechnungslfnr, crechnung.ausstellungsdatum, crechnung.ausstellungsort, crechnung.diagnose, crechnung.bezahlung, crechnung.brutto_summe, crechnung.netto_summe, crechnung.steuerbetrag_zwanzig, crechnung.steuerbetrag_dreizehn, crechnung.steuerbetrag_zehn)
        for crechnungszeile in crechnungszeilen:
            if(crechnungszeile.id):
                update_rechnungszeile(crechnungszeile.id, crechnungszeile.datum, crechnungszeile.artikelcode, crechnungszeile.artikel, crechnungszeile.betrag)
            else:
                crechnungszeile.id = write_rechnungszeile(rechnung_id, crechnungszeile.datum, crechnungszeile.artikelcode, crechnungszeile.artikel, crechnungszeile.betrag)                

        rechnung = read_rechnung(rechnung_id)
        rechnungszeilen = read_rechnungszeilen(rechnung_id)
        html = render_template('ordi/prints/print_rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen, tierhaltung=tierhaltung, adresse=adresse)
        filename = str(rechnung['id']) + "_rechnung_fuer_" + tierhaltung['familienname'] + "_" + tierhaltung['vorname'] + ".pdf"
        path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
        html2pdf(html, path_and_filename)
        return send_file(path_and_filename, as_attachment=True)
        #return redirect(url_for('ordi.edit_rechnung', rechnung_id=rechnung_id))

    datum = date.today().strftime("%Y-%m-%d")
    ort = "Wien"
    return render_template('ordi/rechnung.html', rechnung=None, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, datum=datum, ort=ort, artikelwerte=artikelwerte, page_title="Rechnung")


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
        crechnung, error = fill_and_validate_rechnung(request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        crechnungszeilen, zeilen_error = fill_and_validate_rechnungszeilen(req_rechnungszeilen)
        if(len(error) > 0 or len(zeilen_error) > 0):
            flash(error + zeilen_error)
            return render_template('ordi/rechnung.html', rechnung=rechnung, rechnungszeilen=req_rechnungszeilen, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, artikelwerte=artikelwerte, page_title="Rechnung")

        flag, error = crechnung.calc(crechnungszeilen)
        if(flag == False):
            flash(error)
            return render_template('ordi/rechnung.html', rechnung=rechnung, rechnungszeilen=req_rechnungszeilen, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, artikelwerte=artikelwerte, page_title="Rechnung")
        else:
            update_rechnung(rechnung_id, crechnung.rechnungsjahr, crechnung.rechnungslfnr, crechnung.ausstellungsdatum, crechnung.ausstellungsort, crechnung.diagnose, crechnung.bezahlung, crechnung.brutto_summe, crechnung.netto_summe, crechnung.steuerbetrag_zwanzig, crechnung.steuerbetrag_dreizehn, crechnung.steuerbetrag_zehn)

        for crechnungszeile in crechnungszeilen:
            if(crechnungszeile.id):
                update_rechnungszeile(crechnungszeile.id, crechnungszeile.datum, crechnungszeile.artikelcode, crechnungszeile.artikel, crechnungszeile.betrag)                
            else:
                crechnungszeile.id = write_rechnungszeile(rechnung_id, crechnungszeile.datum, crechnungszeile.artikelcode, crechnungszeile.artikel, crechnungszeile.betrag)

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
    datum = date.today().strftime("%Y-%m-%d")
    return render_template('ordi/rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen, datum=datum, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, artikelwerte=artikelwerte, page_title="Rechnung")


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

