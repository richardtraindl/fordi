

from datetime import date
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from ordi.auth import login_required
from ordi.db import get_db
from ordi.dbaccess import *

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


@bp.route('/create_tierhaltung', methods=('GET', 'POST'))
@login_required
def create_tierhaltung():
    if(request.method == 'POST'):
        error = None

        anredeartcode = request.form['anredeartcode']
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
        geschlechtsartcode = request.form['geschlechtsartcode']
        chip_nummer = request.form['chip_nummer']
        eu_passnummer = request.form['eu_passnummer']
        if(request.form.get('patient')):
            patient = 1
        else:
            patient = 0

        if(len(familienname) == 0):
            error = "Familienname erforderlich"
            flash(error)
            return render_template('ordi/create_tierhaltung.html')
        if(len(tiername) == 0):
            error = "Tiername erforderlich"
            flash(error)
            return render_template('ordi/create_tierhaltung.html')
        if(len(tierart) == 0):
            error = "Tierart erforderlich"
            flash(error)
            return render_template('ordi/create_tierhaltung.html')
        if(len(geburtsdatum) == 0):
            error = "Geburtsdatum erforderlich"
            flash(error)
            return render_template('ordi/create_tierhaltung.html')

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        person_id = cursor.execute(
            'INSERT INTO person (anredeartcode, titel, familienname, vorname, notiz, kunde)'
            ' VALUES (?, ?, ?, ?, ?, ?)',
            (anredeartcode, titel, familienname, vorname, notiz, kunde,)
        ).lastrowid
        dbcon.commit()

        strasse = request.form['strasse']
        postleitzahl = request.form['postleitzahl']
        ort = request.form['ort']
        if(len(strasse) > 0 or len(postleitzahl) > 0 or len(ort) > 0):
            cursor.execute(
                'INSERT INTO adresse (person_id, strasse, postleitzahl, ort)'
                ' VALUES (?, ?, ?, ?)',
                (person_id, strasse, postleitzahl, ort,)
            )
            dbcon.commit()

        kontaktartcode = 1 # fix für Telefon
        kontakt1 = request.form['kontakt1']
        if(len(kontakt1) > 0):
            bad_chars = [';', ':', '-', '/', ' ', '\n']
            kontakt_intern1 = ''.join(i for i in kontakt1 if not i in bad_chars)
            cursor.execute(
                'INSERT INTO kontakt (person_id, kontaktartcode, kontakt, kontakt_intern)'
                ' VALUES (?, ?, ?, ?)',
                (person_id, kontaktartcode, kontakt1, kontakt_intern1,)
            )
            dbcon.commit()
        kontakt2 = request.form['kontakt2']
        if(len(kontakt2) > 0):
            bad_chars = [';', ':', '-', '/', ' ', '\n']
            kontakt_intern2 = ''.join(i for i in kontakt2 if not i in bad_chars)
            cursor.execute(
                'INSERT INTO kontakt (person_id, kontaktartcode, kontakt, kontakt_intern)'
                ' VALUES (?, ?, ?, ?)',
                (person_id, kontaktartcode, kontakt2, kontakt_intern2,)
            )
            dbcon.commit()

        tier_id = cursor.execute(
            'INSERT INTO tier (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient,)
        ).lastrowid
        dbcon.commit()

        id = cursor.execute(
            'INSERT INTO tierhaltung (person_id, tier_id)'
            ' VALUES (?, ?)',
            (person_id, tier_id,)
        ).lastrowid
        dbcon.commit()
        cursor.close()
        return redirect(url_for('ordi.show_tierhaltung', id=id))
    return render_template('ordi/create_tierhaltung.html', new="true", page_title="Neue Karteikarte")


@bp.route('/<int:id>/show_tierhaltung', methods=('GET',))
@login_required
def show_tierhaltung(id):
    tierhaltung = read_tierhaltung(id)

    adresse = read_adresse(tierhaltung['person_id'])

    kontakte = read_kontakte(tierhaltung['person_id'])

    behandlungen = read_behandlungen(id)
    behandlungsdatum = date.today().strftime("%Y-%m-%d")

    return render_template('ordi/tierhaltung.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, behandlungen=behandlungen, behandlungsdatum=behandlungsdatum, page_title="Karteikarte")


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
        geschlechtsartcode = int(request.form['geschlechtsartcode'])
        chip_nummer = request.form['chip_nummer']
        eu_passnummer = request.form['eu_passnummer']
        if(request.form.get('patient')):
            patient = 1
        else:
            patient = 0

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        tier_id = cursor.execute(
            'INSERT INTO tier (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient,)
        ).lastrowid
        dbcon.commit()

        tierhaltung = read_tierhaltung(id)
        newid = cursor.execute(
            'INSERT INTO tierhaltung (person_id, tier_id)'
            ' VALUES (?, ?)',
            (tierhaltung['person_id'], tier_id,)
        ).lastrowid
        dbcon.commit()
        cursor.close()
        return redirect(url_for('ordi.show_tierhaltung', id=newid))
    return render_template('ordi/create_tier.html', new="true", page_title="Neues Tier")


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
        geschlechtsartcode = request.form['geschlechtsartcode']
        chip_nummer = request.form['chip_nummer']
        eu_passnummer = request.form['eu_passnummer']
        if(request.form.get('patient')):
            patient = 1
        else:
            patient = 0

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute(
            'UPDATE tier SET tiername = ?, tierart = ?, rasse = ?, farbe = ?, viren = ?, merkmal = ?, geburtsdatum = ?, geschlechtsartcode = ?, chip_nummer = ?, eu_passnummer = ?, patient = ?'
            ' WHERE tier.id = ?',
            (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient, tier_id,)
        )
        dbcon.commit()
        cursor.close()
        return redirect(url_for('ordi.show_tierhaltung', id=id))
    tierhaltung = read_tierhaltung(id)
    return render_template('ordi/edit_tier.html', tierhaltung=tierhaltung, page_title="Tier ändern")


@bp.route('/<int:id>/<int:person_id>/edit_person', methods=('GET', 'POST'))
@login_required
def edit_person(id, person_id):
    if(request.method == 'POST'):
        anredeartcode = request.form['anredeartcode']
        titel = request.form['titel']
        familienname = request.form['familienname']
        vorname = request.form['vorname']
        notiz = request.form['notiz']
        if(request.form.get('kunde')):
            kunde = 1
        else:
            kunde = 0

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute(
            'UPDATE person SET anredeartcode = ?, titel = ?, familienname = ?, vorname = ?, notiz = ?, kunde = ?'
            ' WHERE person.id = ?',
            (anredeartcode, titel, familienname, vorname, notiz, kunde, person_id,)
        )
        dbcon.commit()

        strasse = request.form['strasse']
        postleitzahl = request.form['postleitzahl']
        ort = request.form['ort']
        adresse = read_adresse(person_id)
        if(adresse):
            if(len(strasse) > 0 or len(postleitzahl) > 0 or len(ort) > 0):
                cursor.execute(
                    'UPDATE adresse SET strasse = ?, postleitzahl = ?, ort = ?'
                    ' WHERE id = ?',
                    (strasse, postleitzahl, ort, adresse['id'],)
                )
                dbcon.commit()
            else:
                cursor.execute('DELETE FROM adresse WHERE id = ?', (adresse['id'],))
                dbcon.commit()
        else:
            if(len(strasse) > 0 or len(postleitzahl) > 0 or len(ort) > 0):
                cursor.execute(
                    'INSERT INTO adresse (person_id, strasse, postleitzahl, ort)'
                    ' VALUES (?, ?, ?, ?)',
                    (person_id, strasse, postleitzahl, ort,)
                )
                dbcon.commit()

        kontakte = read_kontakte(person_id)
        kontaktartcode = 1 # fix für Telefon
        bad_chars = [';', ':', '-', '/', ' ', '\n']
        kontakt1 = request.form['kontakt1']
        kontakt_intern1 = ''.join(i for i in kontakt1 if not i in bad_chars)
        if(len(kontakte) > 0):
            if(len(kontakt1) > 0):
                cursor.execute(
                    'UPDATE kontakt SET kontaktartcode = ?, kontakt = ?, kontakt_intern = ?'
                    ' WHERE id = ?',
                    (kontaktartcode, kontakt1, kontakt_intern1, kontakte[0]['id'],)
                )
                dbcon.commit()
            else:
                cursor.execute('DELETE FROM kontakt WHERE id = ?', (kontakte[0]['id'],))
                dbcon.commit()
        else:
            if(len(kontakt1) > 0):
                cursor.execute(
                    'INSERT INTO kontakt (person_id, kontaktartcode, kontakt, kontakt_intern)'
                    ' VALUES (?, ?, ?, ?)',
                    (person_id, kontaktartcode, kontakt1, kontakt_intern1,)
                )
                dbcon.commit()

        kontakt2 = request.form['kontakt2']
        kontakt_intern2 = ''.join(i for i in kontakt2 if not i in bad_chars)
        if(len(kontakte) > 1):
            if(len(kontakt2) > 0):
                cursor.execute(
                    'UPDATE kontakt SET kontaktartcode = ?, kontakt = ?, kontakt_intern = ?'
                    ' WHERE id = ?',
                    (kontaktartcode, kontakt2, kontakt_intern2, kontakte[1]['id'],)
                )
                dbcon.commit()
            else:
                cursor.execute('DELETE FROM kontakt WHERE id = ?', (kontakte[1]['id'],))
                dbcon.commit()
        else:
            if(len(kontakt2) > 0):
                cursor.execute(
                    'INSERT INTO kontakt (person_id, kontaktartcode, kontakt, kontakt_intern)'
                    ' VALUES (?, ?, ?, ?)',
                    (person_id, kontaktartcode, kontakt2, kontakt_intern2,)
                )
                dbcon.commit()
        cursor.close()
        return redirect(url_for('ordi.show_tierhaltung', id=id))
    tierhaltung = read_tierhaltung(id)
    adresse = read_adresse(person_id)
    kontakte = read_kontakte(person_id)
    return render_template('ordi/edit_person.html', tierhaltung=tierhaltung, adresse=adresse, kontakte=kontakte, page_title="Person ändern")


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

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute(
            'SELECT * FROM tierhaltung WHERE id = ?',
            (id,)
        )
        tierhaltung = cursor.fetchone()

        cursor.execute(
            'INSERT INTO behandlung (tier_id, behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (tierhaltung['tier_id'], behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern,)
        )
        dbcon.commit()
        cursor.close()
    return redirect(url_for('ordi.show_tierhaltung', id=id))


def build_objects(data):
    objects = []
    for idx in range(len(data[0])):
        item = []
        for row in data:
            item.append(row[idx])
        objects.append(item)
    return objects

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
        behandlungen = build_objects(data)

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")

        cursor.execute(
            'SELECT * FROM tierhaltung WHERE id = ?',
            (id,)
        )
        tierhaltung = cursor.fetchone()

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
                    cursor.execute(
                        'INSERT INTO behandlung (tier_id, behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern)'
                        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (tierhaltung['tier_id'], behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern,)
                    )
                    dbcon.commit()
                else:
                    cursor.execute(
                        'UPDATE behandlung SET behandlungsdatum = ?, gewicht = ?, diagnose = ?, laborwerte1 = ?, laborwerte2 = ?, arzneien = ?, arzneimittel = ?, impfungen_extern = ?'
                        ' WHERE behandlung.id = ?',
                        (behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern, behandlung_id)
                    )
                    dbcon.commit()
        cursor.close()
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
        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        behandlungsverlauf_id = cursor.execute(
            'INSERT INTO behandlungsverlauf (tierhaltung_id, datum, diagnose, behandlung)'
            ' VALUES (?, ?, ?, ?)',
            (tierhaltung['id'], datum, diagnose, behandlung,)
        ).lastrowid
        dbcon.commit()
        cursor.close()
        return redirect(url_for('ordi.edit_behandlungsverlauf', behandlungsverlauf_id=behandlungsverlauf_id))
    else:
        tierhaltung = read_tierhaltung(id)
    return render_template('ordi/behandlungsverlauf.html', tierhaltung=tierhaltung, page_title="Behandlungsverlauf")


@bp.route('/<int:behandlungsverlauf_id>/edit_behandlungsverlauf', methods=('GET', 'POST'))
@login_required
def edit_behandlungsverlauf(behandlungsverlauf_id):
    if(request.method == 'POST'):
        datum = request.form['datum']
        if(len(datum) == 0):
            datum = date.today().strftime("%Y-%m-%d")
        diagnose = request.form['diagnose']
        behandlung = request.form['behandlung']

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute(
            'UPDATE behandlungsverlauf SET datum = ?, diagnose = ?, behandlung = ?'
            ' WHERE id = ?',
            (datum, diagnose, behandlung, behandlungsverlauf_id,)
        )
        dbcon.commit()
        cursor.close()
    behandlungsverlauf = read_behandlungsverlauf(behandlungsverlauf_id)
    tierhaltung = read_tierhaltung(behandlungsverlauf['tierhaltung_id'])
    return render_template('ordi/behandlungsverlauf.html', behandlungsverlauf_id=behandlungsverlauf_id, behandlungsverlauf=behandlungsverlauf, tierhaltung=tierhaltung, page_title="Behandlungsverlauf")


@bp.route('/<int:id>/create_rechnung', methods=('GET', 'POST'))
@login_required
def create_rechnung(id):
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

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")

        rechnung_id = cursor.execute(
            'INSERT INTO rechnung (tierhaltung_id, rechnungsjahr, rechnungslfnr, ausstellungsdatum, ausstellungsort, diagnose, bezahlung,'
            ' brutto_summe, netto_summe, steuerbetrag_zwanzig, steuerbetrag_dreizehn, steuerbetrag_zehn)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (id, rechnungsjahr, rechnungslfnr, ausstellungsdatum, ausstellungsort, diagnose, bezahlung, brutto_summe, netto_summe, steuerbetrag_zwanzig, steuerbetrag_dreizehn, steuerbetrag_zehn,)
        ).lastrowid
        dbcon.commit()

        data = (
            request.form.getlist('datum[]'),
            request.form.getlist('artikelartcode[]'),
            request.form.getlist('artikel[]'),
            request.form.getlist('betrag[]'),
            request.form.getlist('rechnungszeile_id[]')
        )
        rechnungen = build_objects(data)
        print(rechnungen)

        cursor.execute(
            'SELECT * FROM tierhaltung WHERE id = ?',
            (id,)
        )
        tierhaltung = cursor.fetchone()

        for rechnung in rechnungen:
            datum = rechnung[0]
            if(len(datum) == 0):
                datum = date.today().strftime("%Y-%m-%d")
            artikelartcode = rechnung[1]
            artikel = rechnung[2]
            betrag = rechnung[3]
            rechnungszeile_id = rechnung[4]
            if(len(artikelartcode) > 0 or len(artikel) > 0 or len(betrag) > 0):
                if(len(rechnungszeile_id) == 0):
                    cursor.execute(
                        'INSERT INTO rechnungszeile (rechnung_id, datum, artikelartcode, artikel, betrag)'
                        ' VALUES (?, ?, ?, ?, ?)',
                        (rechnung_id, datum, artikelartcode, artikel, betrag,)
                    )
                    dbcon.commit()
                else:
                    cursor.execute(
                        'UPDATE rechnungszeile SET datum = ?, artikelartcode = ?, artikel = ?, betrag = ?'
                        ' WHERE rechnungszeile.id = ?',
                        (datum, artikelartcode, artikel, betrag, rechnungszeile_id,)
                    )
                    dbcon.commit()

        cursor.close()
        return redirect(url_for('ordi.edit_rechnung', rechnung_id=rechnung_id,))
    tierhaltung = read_tierhaltung(id)
    rechnungszeile_datum = date.today().strftime("%Y-%m-%d")
    ausstellungsdatum = date.today().strftime("%Y-%m-%d")
    ausstellungsort = "Wien"
    return render_template('ordi/rechnung.html', tierhaltung=tierhaltung, ausstellungsdatum=ausstellungsdatum, ausstellungsort=ausstellungsort, rechnungszeile_datum=rechnungszeile_datum, page_title="Rechnung")


@bp.route('/<int:rechnung_id>/edit_rechnung', methods=('GET', 'POST'))
@login_required
def edit_rechnung(rechnung_id):
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

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute(
            'UPDATE rechnung SET rechnungsjahr = ?, rechnungslfnr = ?, ausstellungsdatum = ?, ausstellungsort = ?, diagnose = ?, bezahlung = ?'
            ' WHERE id = ?',
            (rechnungsjahr, rechnungslfnr, ausstellungsdatum, ausstellungsort, diagnose, bezahlung, rechnung_id,)
        )
        dbcon.commit()

        data = (
            request.form.getlist('datum[]'),
            request.form.getlist('artikelartcode[]'),
            request.form.getlist('artikel[]'),
            request.form.getlist('betrag[]'),
            request.form.getlist('rechnungszeile_id[]')
        )
        rechnungen = build_objects(data)
        for rechnung in rechnungen:
            datum = rechnung[0]
            artikelartcode = rechnung[1]
            artikel = rechnung[2]
            betrag = rechnung[3]
            rechnungszeile_id = rechnung[4]
            if(len(artikelartcode) > 0 or len(artikel) > 0 or len(betrag) > 0):
                if(len(rechnungszeile_id) == 0):
                    cursor.execute(
                        'INSERT INTO rechnungszeile (rechnung_id, datum, artikelartcode, artikel, betrag)'
                        ' VALUES (?, ?, ?, ?, ?)',
                        (rechnung_id, datum, artikelartcode, artikel, betrag,)
                    )
                    dbcon.commit()
                else:
                    cursor.execute(
                        'UPDATE rechnungszeile SET datum = ?, artikelartcode = ?, artikel = ?, betrag = ?'
                        ' WHERE rechnungszeile.id = ?',
                        (datum, artikelartcode, artikel, betrag, rechnungszeile_id,)
                    )
                    dbcon.commit()

        cursor.close()
    rechnungszeile_datum = date.today().strftime("%Y-%m-%d")
    rechnungszeilen = read_rechnungszeilen(rechnung_id)
    rechnung = read_rechnung(rechnung_id)
    tierhaltung = read_tierhaltung(rechnung['tierhaltung_id'])
    return render_template('ordi/rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen, rechnungszeile_datum=rechnungszeile_datum, tierhaltung=tierhaltung, page_title="Rechnung")


@bp.route('/<int:id>/delete_tierhaltung', methods=('GET',))
@login_required
def delete_tierhaltung(id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('DELETE FROM tierhaltung WHERE id = ?', (id,))
    dbcon.commit()
    cursor.close()
    return redirect(url_for('ordi.index'))

