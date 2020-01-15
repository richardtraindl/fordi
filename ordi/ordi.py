

from datetime import date
import re, os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from ordi.auth import login_required
from ordi.db import get_db
from ordi.dbaccess import *
from ordi.business import *
from ordi.values import *

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
        anredecode = request.form['anredecode']
        titel = request.form['titel']
        familienname = request.form['familienname']
        vorname = request.form['vorname']
        notiz = request.form['notiz']
        if(request.form.get('kunde')):
            kunde = 1
        else:
            kunde = 0

        tiername = request.form['tiername']
        tierart = request.form['tierart']
        rasse = request.form['rasse']
        farbe = request.form['farbe']
        viren = request.form['viren']
        merkmal = request.form['merkmal']
        geburtsdatum = request.form['geburtsdatum']
        geschlechtscode = request.form['geschlechtscode']
        chip_nummer = request.form['chip_nummer']
        eu_passnummer = request.form['eu_passnummer']
        if(request.form.get('patient')):
            patient = 1
        else:
            patient = 0

        error = ""
        if(len(familienname) == 0):
            error += "Familienname erforderlich. "
        if(len(tiername) == 0):
            error += "Tiername erforderlich. "
        if(len(tierart) == 0):
            error += "Tierart erforderlich. "
        if(len(geburtsdatum) == 0):
            error += "Geburtsdatum erforderlich. "
        if(len(error) > 0):
            flash(error)
            return render_template('ordi/create_tierhaltung.html')

        person_id = write_person(anredecode, titel, familienname, vorname, notiz, kunde)

        tier_id = write_tier(tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtscode, chip_nummer, eu_passnummer, patient)

        strasse = request.form['strasse']
        postleitzahl = request.form['postleitzahl']
        ort = request.form['ort']
        if(len(strasse) > 0 or len(postleitzahl) > 0 or len(ort) > 0):
            write_adresse(person_id, strasse, postleitzahl, ort)

        kontaktartcode = 1 # fix für Telefon
        kontakt1 = request.form['kontakt1']
        if(len(kontakt1) > 0):
            bad_chars = [';', ':', '-', '/', ' ', '\n']
            kontakt_intern1 = ''.join(i for i in kontakt1 if not i in bad_chars)
            write_kontakt(person_id, kontaktartcode, kontakt1, kontakt_intern1)

        kontakt2 = request.form['kontakt2']
        if(len(kontakt2) > 0):
            bad_chars = [';', ':', '-', '/', ' ', '\n']
            kontakt_intern2 = ''.join(i for i in kontakt2 if not i in bad_chars)
            write_kontakt(person_id, kontaktartcode, kontakt2, kontakt_intern2)

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
        tiername = request.form['tiername']
        tierart = request.form['tierart']
        rasse = request.form['rasse']
        farbe = request.form['farbe']
        viren = request.form['viren']
        merkmal = request.form['merkmal']
        geburtsdatum = request.form['geburtsdatum']
        geschlechtscode = int(request.form['geschlechtscode'])
        chip_nummer = request.form['chip_nummer']
        eu_passnummer = request.form['eu_passnummer']
        if(request.form.get('patient')):
            patient = 1
        else:
            patient = 0

        tier_id = write_tier(tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtscode, chip_nummer, eu_passnummer, patient)
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
        tiername = request.form['tiername']
        tierart = request.form['tierart']
        rasse = request.form['rasse']
        farbe = request.form['farbe']
        viren = request.form['viren']
        merkmal = request.form['merkmal']
        geburtsdatum = request.form['geburtsdatum']
        geschlechtscode = request.form['geschlechtscode']
        chip_nummer = request.form['chip_nummer']
        eu_passnummer = request.form['eu_passnummer']
        if(request.form.get('patient')):
            patient = 1
        else:
            patient = 0

        update_tier(tier_id, tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtscode, chip_nummer, eu_passnummer, patient)
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
        anredecode = request.form['anredecode']
        titel = request.form['titel']
        familienname = request.form['familienname']
        vorname = request.form['vorname']
        notiz = request.form['notiz']
        if(request.form.get('kunde')):
            kunde = 1
        else:
            kunde = 0
        update_person(person_id, anredecode, titel, familienname, vorname, notiz, kunde)

        strasse = request.form['strasse']
        postleitzahl = request.form['postleitzahl']
        ort = request.form['ort']
        adresse = read_adresse(person_id)
        if(adresse):
            if(len(strasse) > 0 or len(postleitzahl) > 0 or len(ort) > 0):
                update_adresse(adresse['id'], strasse, postleitzahl, ort)
            else:
                delete_db_adresse(adresse['id'])
        else:
            if(len(strasse) > 0 or len(postleitzahl) > 0 or len(ort) > 0):
                write_adresse(person_id, strasse, postleitzahl, ort)

        kontakte = read_kontakte(person_id)
        kontaktartcode = 1 # fix für Telefon
        bad_chars = [';', ':', '-', '/', ' ', '\n']
        kontakt1 = request.form['kontakt1']
        kontakt_intern1 = ''.join(i for i in kontakt1 if not i in bad_chars)
        if(len(kontakte) > 0):
            if(len(kontakt1) > 0):
                update_kontakt(kontakte[0]['id'], kontaktartcode, kontakt1, kontakt_intern1)
            else:
                delete_db_kontakt(kontakte[0]['id'])
        else:
            if(len(kontakt1) > 0):
                write_kontakt(person_id, kontaktartcode, kontakt1, kontakt_intern1)

        kontakt2 = request.form['kontakt2']
        kontakt_intern2 = ''.join(i for i in kontakt2 if not i in bad_chars)
        if(len(kontakte) > 1):
            if(len(kontakt2) > 0):
                update_kontakt(kontakte[1]['id'], kontaktartcode, kontakt2, kontakt_intern2)
            else:
                delete_db_kontakt(kontakte[1]['id'])
        else:
            if(len(kontakt2) > 0):
                write_kontakt(person_id, kontaktartcode, kontakt2, kontakt_intern2)
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
        error = None
        behandlungsdatum = request.form['behandlungsdatum']
        gewicht = request.form['gewicht']
        diagnose = request.form['diagnose']
        laborwerte1 = request.form['laborwerte1']
        laborwerte2 = request.form['laborwerte2']
        arzneien = request.form['arzneien']
        arzneimittel = request.form['arzneimittel']
        impfungen_extern = request.form['impfungen_extern']

        if(len(gewicht) == 0 and len(diagnose) == 0 and len(laborwerte1) == 0 and
           len(laborwerte2) == 0 and len(arzneien) == 0 and len(arzneimittel) == 0 and
           len(impfungen_extern) == 0):
            return redirect(url_for('ordi.show_tierhaltung', id=id))

        if(len(behandlungsdatum) == 0):
            behandlungsdatum = date.today().strftime("%Y-%m-%d")
            #good_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            #behandlungsdatum = ''.join(i for i in request.form['behandlungsdatum'] if i in good_chars)

        if(len(gewicht) > 0 and re.search(r"\d", gewicht) == None):
            error = "Zahl für Gewicht erforderlich."
            flash(error)
            tierhaltung = read_tierhaltung(id)
            adresse = read_adresse(tierhaltung['person_id'])
            kontakte = read_kontakte(tierhaltung['person_id'])
            behandlungen = read_behandlungen(id)
            return render_template('ordi/show_tierhaltung.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, behandlungen=behandlungen)

        tierhaltung = read_tierhaltung(id)
        behandlung_id = write_behandlung(tierhaltung['tier_id'], behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern)
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
        data = (
            request.form.getlist('behandlungsdatum[]'),
            request.form.getlist('diagnose[]'),
            request.form.getlist('laborwerte1[]'),
            request.form.getlist('laborwerte2[]'),
            request.form.getlist('arzneien[]'),
            request.form.getlist('arzneimittel[]'),
            request.form.getlist('impfungen_extern[]'),
            request.form.getlist('gewicht[]'),
            request.form.getlist('behandlung_id[]'),
        )
        behandlungen = build_behandlungen(data)
        tierhaltung = read_tierhaltung(id)

        for behandlung in behandlungen:
            behandlungsdatum = behandlung[0]
            diagnose = behandlung[1]
            laborwerte1 = behandlung[2]
            laborwerte2 = behandlung[3]
            arzneien = behandlung[4]
            arzneimittel = behandlung[5]
            impfungen_extern = behandlung[6]
            gewicht = behandlung[7]
            behandlung_id = behandlung[8]
            if(len(gewicht) > 0 or len(diagnose) > 0 or len(laborwerte1) > 0 or
               len(laborwerte2) > 0 or len(arzneien) > 0 or len(arzneimittel) > 0 or
               len(impfungen_extern) > 0):
                if(len(behandlung_id) == 0):
                    behandlung_id = write_behandlung(tierhaltung['tier_id'], behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern)
                else:
                    update_behandlung(behandlung_id, behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern)
            if(len(impfungen_extern) > 0):
                impfungstexte = impfungen_extern.split(',')
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
        kontakte = read_kontakte(behandlungsverlauf['person_id'])
        behandlungsverlauf_id = write_behandlungsverlauf(tierhaltung['person_id'], tierhaltung['tier_id'], datum, diagnose, behandlung)
        behandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
        html = render_template('ordi/prints/print_behandlungsverlauf.html', tierhaltung=tierhaltung, adresse=adresse, behandlungsverlauf=behandlungsverlauf)
        file = open('c:\\temp\\behandlungsverlauf.html', 'w')
        file.write(html)
        file.close()
        cmd = "c:\\eprog\\wkhtmltopdf\\bin\\wkhtmltopdf.exe c:\\temp\\behandlungsverlauf.html c:\\temp\\behandlungsverlauf.pdf"
        os.system(cmd)
        return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, tierhaltung=tierhaltung, adresse=adresse, kontakte=kon
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
        kontakte = read_kontakte(behandlungsverlauf['person_id'])
        html = render_template('ordi/prints/print_behandlungsverlauf.html', tierhaltung=tierhaltung, adresse=adresse, behandlungsverlauf=behandlungsverlauf)
        file = open('c:\\temp\\behandlungsverlauf.html', 'w')
        file.write(html)
        file.close()
        cmd = "c:\\eprog\\wkhtmltopdf\\bin\\wkhtmltopdf.exe c:\\temp\\behandlungsverlauf.html c:\\temp\\behandlungsverlauf.pdf"
        os.system(cmd)
        return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, page_title="Behandlungsverlauf")
    behandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
    tierhaltung = read_tierhaltung_by_children(behandlungsverlauf['person_id'], behandlungsverlauf['tier_id'])
    adresse = read_adresse(behandlungsverlauf['person_id'])
    kontakte = read_kontakte(behandlungsverlauf['person_id'])
    return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, page_title="Behandlungsverlauf")


def build_rechnungszeilen(data):
    rechnungszeilen = []
    for idx in range(len(data[0])):
        rechnungszeile = []
        for row in data:
            rechnungszeile.append(row[idx])
        if(rechnungszeile[1] == "0" and len(rechnungszeile[2]) == 0 and
           len(rechnungszeile[3]) == 0 and len(rechnungszeile[4]) == 0):
            continue
        else:
            rechnungszeilen.append(rechnungszeile)
    return rechnungszeilen

@bp.route('/<int:id>/create_rechnung', methods=('GET', 'POST'))
@login_required
def create_rechnung(id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])
    if(request.method == 'POST'):
        rechnungsjahr = request.form['rechnungsjahr']
        rechnungslfnr = request.form['rechnungslfnr']
        ausstellungsdatum = request.form['ausstellungsdatum']
        if(len(ausstellungsdatum) == 0):
            ausstellungsdatum = date.today().strftime("%Y-%m-%d")
        ausstellungsort = request.form['ausstellungsort']
        if(len(ausstellungsort) == 0):
            ausstellungsort = "Wien"
        diagnose = request.form['diagnose']
        bezahlung = request.form['bezahlung']
        brutto_summe = 0
        netto_summe = 0
        steuerbetrag_zwanzig = 0
        steuerbetrag_dreizehn = 0
        steuerbetrag_zehn = 0

        data = (
            request.form.getlist('datum[]'),
            request.form.getlist('artikelcode[]'),
            request.form.getlist('artikel[]'),
            request.form.getlist('betrag[]'),
            request.form.getlist('rechnungszeile_id[]')
        )
        req_rechnungszeilen = build_rechnungszeilen(data)
        calc = calc_rechnung(req_rechnungszeilen)
        if(len(calc.error_msg) > 0):
            flash(calc.error_msg)
            tierhaltung = read_tierhaltung(id)
            adresse = read_adresse(tierhaltung['person_id'])
            kontakte = read_kontakte(tierhaltung['person_id'])
            return render_template('ordi/rechnung.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, req_rechnungszeilen=req_rechnungszeilen, artikelwerte=artikelwerte, page_title="Rechnung")

        tierhaltung = read_tierhaltung(id)
        rechnung_id = write_rechnung(tierhaltung['person_id'], tierhaltung['tier_id'], rechnungsjahr, rechnungslfnr, ausstellungsdatum, ausstellungsort, diagnose, bezahlung, calc.brutto_summe, calc.netto_summe, calc.steuerbetrag_zwanzig, calc.steuerbetrag_dreizehn, calc.steuerbetrag_zehn)

        for req_rechnungszeile in req_rechnungszeilen:
            datum = req_rechnungszeile[0]
            if(len(datum) == 0):
                datum = date.today().strftime("%Y-%m-%d")
            artikelcode = req_rechnungszeile[1]
            artikel = req_rechnungszeile[2]
            betrag = req_rechnungszeile[3]
            rechnungszeile_id = req_rechnungszeile[4]
            if(len(artikelcode) > 0 or len(artikel) > 0 or len(betrag) > 0):
                if(len(rechnungszeile_id) == 0):
                    write_rechnungszeile(rechnung_id, datum, artikelcode, artikel, betrag)
                else:
                    update_rechnungszeile(rechnungszeile_id, datum, artikelcode, artikel, betrag)
        return redirect(url_for('ordi.edit_rechnung', rechnung_id=rechnung_id,))
    tierhaltung = read_tierhaltung(id)
    adresse = read_adresse(tierhaltung['person_id'])
    kontakte = read_kontakte(tierhaltung['person_id'])
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
    if(request.method == 'POST'):
        rechnungsjahr = request.form['rechnungsjahr']
        rechnungslfnr = request.form['rechnungslfnr']
        ausstellungsdatum = request.form['ausstellungsdatum']
        if(len(ausstellungsdatum) == 0):
            ausstellungsdatum = date.today().strftime("%Y-%m-%d")
        ausstellungsort = request.form['ausstellungsort']
        if(len(ausstellungsort) == 0):
            ausstellungsort = "Wien"
        diagnose = request.form['diagnose']
        bezahlung = request.form['bezahlung']
        brutto_summe = 0
        netto_summe = 0
        steuerbetrag_zwanzig = 0
        steuerbetrag_dreizehn = 0
        steuerbetrag_zehn = 0

        data = (
            request.form.getlist('datum[]'),
            request.form.getlist('artikelcode[]'),
            request.form.getlist('artikel[]'),
            request.form.getlist('betrag[]'),
            request.form.getlist('rechnungszeile_id[]')
        )
        req_rechnungszeilen = build_rechnungszeilen(data)
        calc = calc_rechnung(req_rechnungszeilen)
        if(len(calc.error_msg) > 0):
            flash(calc.error_msg)
            rechnung = read_rechnung(rechnung_id)
            tierhaltung = read_tierhaltung_by_children(rechnung['person_id'], rechnung['tier_id'])
            adresse = read_adresse(tierhaltung['person_id'])
            kontakte = read_kontakte(tierhaltung['person_id'])
            return render_template('ordi/rechnung.html', rechnung_id=rechnung_id, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, req_rechnungszeilen=req_rechnungszeilen, artikelwerte=artikelwerte, page_title="Rechnung")
        else:
            update_rechnung(rechnung_id, rechnungsjahr, rechnungslfnr, ausstellungsdatum, ausstellungsort, diagnose, bezahlung, calc.brutto_summe, calc.netto_summe, calc.steuerbetrag_zwanzig, calc.steuerbetrag_dreizehn, calc.steuerbetrag_zehn)

        for req_rechnungszeile in req_rechnungszeilen:
            datum = req_rechnungszeile[0]
            if(len(datum) == 0):
                datum = date.today().strftime("%Y-%m-%d")
            artikelcode = req_rechnungszeile[1]
            artikel = req_rechnungszeile[2]
            betrag = req_rechnungszeile[3]
            rechnungszeile_id = req_rechnungszeile[4]
            if(len(datum) == 10 and len(artikelcode) > 0 and len(betrag) > 0):
                if(len(rechnungszeile_id) == 0):
                    write_rechnungszeile(rechnung_id, datum, artikelcode, artikel, betrag)
                else:
                    update_rechnungszeile(rechnungszeile_id, datum, artikelcode, artikel, betrag)
    rechnungszeile_datum = date.today().strftime("%Y-%m-%d")
    rechnungszeilen = read_rechnungszeilen(rechnung_id)
    rechnung = read_rechnung(rechnung_id)
    tierhaltung = read_tierhaltung_by_children(rechnung['person_id'], rechnung['tier_id'])
    adresse = read_adresse(tierhaltung['person_id'])
    kontakte = read_kontakte(tierhaltung['person_id'])
    return render_template('ordi/rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen, rechnungszeile_datum=rechnungszeile_datum, tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, artikelwerte=artikelwerte, page_title="Rechnung")


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

