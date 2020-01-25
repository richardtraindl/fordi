

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

        write_person(cperson)
        write_tier(ctier)

        cadresse = fill_and_validate_adresse(request)[0]
        if(len(cadresse.strasse) > 0 or len(cadresse.postleitzahl) > 0 or len(cadresse.ort) > 0):
            write_adresse(cadresse)

        ckontakte = fill_and_validate_kontakte(request)[0]
        for ckontakt in ckontakte:
            if(len(ckontakt.kontakt) > 0):
                ckontakt.id = write_kontakt(ckontakt)

        ctierhaltung = cTierhaltung(None, cperson.id, ctier.id)
        write_tierhaltung(ctierhaltung)
        return redirect(url_for('ordi.show_tierhaltung', id=ctierhaltung.id))

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
    ctierhaltung, cperson, ctier = read_tierhaltung(id)
    cperson.adresse = read_adresse_for_person(cperson.id)
    cperson.kontakte = read_kontakte_for_person(cperson.id)
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
                           anredewerte=anredewerte, geschlechtswerte=geschlechtswerte, laboreferenzen=laboreferenzen, 
                           impfungswerte=impfungswerte, page_title="Karteikarte")


@bp.route('/<int:id>/create_tier', methods=('GET', 'POST'))
@login_required
def create_tier(id):
    if(request.method == 'POST'):
        ctier, error = fill_and_validate_tier(request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/create_tier.html', id=id)
        write_tier(ctier)
        ctierhaltung = read_tierhaltung(id)[0]
        new_ctierhaltung = cTierhaltung(None, ctierhaltung.person_id, ctier.id)
        write_tierhaltung(new_ctierhaltung)
        return redirect(url_for('ordi.show_tierhaltung', id=new_ctierhaltung.id))

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
        update_tier(ctier)
        return redirect(url_for('ordi.show_tierhaltung', id=id))

    ctierhaltung, cperson, ctier = read_tierhaltung(id)
    geschlechtswerte = []
    for key, value in GESCHLECHT.items():
        geschlechtswerte.append([key, value])
    return render_template('ordi/edit_tier.html', id=id, tier=ctier, geschlechtswerte=geschlechtswerte, page_title="Tier ändern")


@bp.route('/<int:id>/<int:person_id>/edit_person', methods=('GET', 'POST'))
@login_required
def edit_person(id, person_id):
    if(request.method == 'POST'):
        cperson, error = fill_and_validate_person(request)
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/edit_person.html', id=id, person_id=person_id)
        update_person(cperson)

        cadresse = fill_and_validate_adresse(request)[0]
        if(len(cadresse.strasse) > 0 or len(cadresse.postleitzahl) > 0 or len(cadresse.ort) > 0):
            if(cadresse.id):
                update_adresse(cadresse)
            else:
                write_adresse(cadresse)
        else:
            if(cadresse.id):
                delete_db_adresse(cadresse.id)

        ckontakte = fill_and_validate_kontakte(request)[0]
        for ckontakt in ckontakte:
            if(len(ckontakt.kontakt) > 0):
                if(ckontakt.id):
                    update_kontakt(ckontakt)
                else:
                    write_kontakt(ckontakt)
            else:
                if(ckontakt.id):
                    delete_db_kontakt(ckontakt.id)
        return redirect(url_for('ordi.show_tierhaltung', id=id))

    ctierhaltung, cperson, ctier = read_tierhaltung(id)
    cadresse = read_adresse_for_person(cperson.id)
    ckontakte = read_kontakte_for_person(cperson.id)
    anredewerte = []
    for key, value in ANREDE.items():
        anredewerte.append([key, value])
    return render_template('ordi/edit_person.html', id=id, person=cperson, anredewerte=anredewerte, page_title="Person ändern")


@bp.route('/<int:id>/save_behandlungen', methods=('GET', 'POST'))
@login_required
def save_behandlungen(id):
    if(request.method == 'POST'):
        req_behandlungen = build_behandlungen(request)
        cbehandlungen, error = fill_and_validate_behandlungen(req_behandlungen)
        if(len(error) > 0):
            flash(error)
            ctierhaltung, cperson, ctier = read_tierhaltung(id)
            cperson.adresse = read_adresse_for_person(cperson.id)
            cperson.kontakte = read_kontakte_for_person(cperson.id)
            return render_template('ordi/tierhaltung.html', id=id, person=cperson, tier=ctier, behandlungen=req_behandlungen)

        ctierhaltung = read_tierhaltung(id)[0]
        for cbehandlung in cbehandlungen:
            if(cbehandlung.id):
                update_behandlung(cbehandlung)
            else:
                cbehandlung.tier_id = ctierhaltung.tier_id
                write_behandlung(cbehandlung)
            if(len(cbehandlung.impfungen_extern) > 0):
                impfungstexte = cbehandlung.impfungen_extern.split(',')
            else:
                impfungstexte = []
            save_or_delete_impfungen(cbehandlung.id, impfungstexte)
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
        ctierhaltung, cperson, ctier = read_tierhaltung(id)
        cperson.adresse = read_adresse_for_person(ctierhaltung.person_id)
        behandlungsverlauf_id = write_behandlungsverlauf(cperson.id, ctier.id, datum, diagnose, behandlung)
        behandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
        html = render_template('ordi/prints/print_behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, person=cperson, tier=ctier)
        filename = str(behandlungsverlauf['id']) + "_behandlungsverlauf_fuer_" + cperson.familienname + "_" + cperson.vorname + ".pdf"
        path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
        html2pdf(html, path_and_filename)
        return send_file(path_and_filename, as_attachment=True)
    else:
        ctierhaltung, cperson, ctier = read_tierhaltung(id)
        cperson.adresse = read_adresse_for_person(cperson.id)
        cperson.kontakte = read_kontakte_for_person(cperson.id)
        datum = date.today().strftime("%Y-%m-%d")
        return render_template('ordi/behandlungsverlauf.html', id=id, person=cperson, tier=ctier, datum=datum, page_title="Behandlungsverlauf")


@bp.route('/<int:behandlungsverlauf_id>/edit_behandlungsverlauf', methods=('GET', 'POST'))
@login_required
def edit_behandlungsverlauf(behandlungsverlauf_id):
    if(request.method == 'POST'):
        datum = request.form['datum']
        """if(len(datum) == 0):
            datum = date.today().strftime("%Y-%m-%d")"""
        diagnose = request.form['diagnose']
        behandlung = request.form['behandlung']
        update_behandlungsverlauf(behandlungsverlauf_id, datum, diagnose, behandlung)
        behandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
        ctierhaltung, cperson, ctier = read_tierhaltung_by_children(behandlungsverlauf['person_id'], behandlungsverlauf['tier_id'])
        cperson.adresse = read_adresse_for_person(cperson.id)
        html = render_template('ordi/prints/print_behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, person=cperson, tier=ctier)
        filename = str(behandlungsverlauf['id']) + "_behandlungsverlauf_fuer_" + cperson.familienname + "_" + cperson.vorname + ".pdf"
        path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
        html2pdf(html, path_and_filename)
        return send_file(path_and_filename, as_attachment=True)
    else:
        behandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
        ctierhaltung, cperson, ctier = read_tierhaltung_by_children(behandlungsverlauf['person_id'], behandlungsverlauf['tier_id'])
        cperson.adresse = read_adresse_for_person(cperson.id)
        cperson.kontakte = read_kontakte_for_person(cperson.id)
    return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, person=cperson, tier=ctier, page_title="Behandlungsverlauf")


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

        crechnung.id = write_rechnung(cperson.id, ctier.id, crechnung.rechnungsjahr, 
                                     crechnung.rechnungslfnr, crechnung.ausstellungsdatum, crechnung.ausstellungsort, 
                                     crechnung.diagnose, crechnung.bezahlung, crechnung.brutto_summe, 
                                     crechnung.netto_summe, crechnung.steuerbetrag_zwanzig, crechnung.steuerbetrag_dreizehn, 
                                     crechnung.steuerbetrag_zehn)

        for crechnungszeile in crechnung.rechnungszeilen:
            if(crechnungszeile.id):
                update_rechnungszeile(crechnungszeile.id, crechnungszeile.datum, crechnungszeile.artikelcode, crechnungszeile.artikel, crechnungszeile.betrag)
            else:
                crechnungszeile.id = write_rechnungszeile(crechnung.id, crechnungszeile.datum, crechnungszeile.artikelcode, crechnungszeile.artikel, crechnungszeile.betrag)

        return redirect(url_for('ordi.edit_rechnung', rechnung_id=crechnung.id))
        #newcrechnung = read_rechnung(crechnung.id)
        #newcrechnung.rechnungszeilen = read_rechnungszeilen_for_rechnung(crechnung.id)
        #html = render_template('ordi/prints/print_rechnung.html', rechnung=newcrechnung, tierhaltung=tierhaltung, adresse=cperson.adresse)
        #filename = str(newcrechnung.id) + "_rechnung_fuer_" + tierhaltung['familienname'] + "_" + tierhaltung['vorname'] + ".pdf"
        #path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
        #html2pdf(html, path_and_filename)
        #return send_file(path_and_filename, as_attachment=True)"""

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
        crechnung.id = rechnung_id
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
        else:
            update_rechnung(rechnung_id, crechnung.rechnungsjahr, crechnung.rechnungslfnr, crechnung.ausstellungsdatum, crechnung.ausstellungsort, crechnung.diagnose, crechnung.bezahlung, crechnung.brutto_summe, crechnung.netto_summe, crechnung.steuerbetrag_zwanzig, crechnung.steuerbetrag_dreizehn, crechnung.steuerbetrag_zehn)

        for rechnungszeile in crechnung.rechnungszeilen:
            if(rechnungszeile.id):
                update_rechnungszeile(rechnungszeile.id, rechnungszeile.datum, rechnungszeile.artikelcode, rechnungszeile.artikel, rechnungszeile.betrag)
            else:
                rechnungszeile.id = write_rechnungszeile(rechnung_id, rechnungszeile.datum, rechnungszeile.artikelcode, rechnungszeile.artikel, rechnungszeile.betrag)

        return redirect(url_for('ordi.edit_rechnung', rechnung_id=rechnung_id))
        #crechnung = read_rechnung(rechnung_id)
        #crechnung.rechnungszeilen = read_rechnungszeilen_for_rechnung(rechnung_id)
        #html = render_template('ordi/prints/print_rechnung.html', rechnung=crechnung, tierhaltung=tierhaltung, adresse=cperson.adresse)
        #filename = str(crechnung.id) + "_rechnung_fuer_" + tierhaltung['familienname'] + "_" + tierhaltung['vorname'] + ".pdf"
        #path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)
        #html2pdf(html, path_and_filename)
        #return send_file(path_and_filename, as_attachment=True)

    crechnung = read_rechnung(rechnung_id)
    crechnung.rechnungszeilen = read_rechnungszeilen_for_rechnung(rechnung_id)
    return render_template('ordi/rechnung.html', rechnung=crechnung, rechnungszeilen=crechnung.rechnungszeilen, artikelwerte=artikelwerte, 
                            id=ctierhaltung.id, person=cperson, tier=ctier, page_title="Rechnung")


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
    crechnungszeile = read_rechnungszeile(rechnungszeile_id)
    delete_db_rechnungszeile(rechnungszeile_id)
    return redirect(url_for('ordi.edit_rechnung', rechnung_id=crechnungszeile.rechnung_id))


@bp.route('/<int:id>/delete_tierhaltung', methods=('GET',))
@login_required
def delete_tierhaltung(id):
    delete_db_tierhaltung(id)
    return redirect(url_for('ordi.index'))

