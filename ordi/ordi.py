

from datetime import date

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from ordi.auth import login_required
from ordi.db import get_db

bp = Blueprint('ordi', __name__)


@bp.route('/', methods=('GET',))
@login_required
def index():
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM tierhaltung, person, tier WHERE tierhaltung.person_id = person.id AND tierhaltung.tier_id = tier.id'
        ' ORDER BY familienname ASC'
    )
    tierhaltungen = cursor.fetchall()
    return render_template('ordi/index.html', tierhaltungen=tierhaltungen)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
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
        person_id = cursor.execute(
            'INSERT INTO person (anredeartcode, titel, familienname, vorname, notiz, kunde)'
            ' VALUES (?, ?, ?, ?, ?, ?)',
            (anredeartcode, titel, familienname, vorname, notiz, kunde)
        ).lastrowid
        dbcon.commit()

        strasse = request.form['strasse']
        postleitzahl = request.form['postleitzahl']
        ort = request.form['ort']
        adresse_id = cursor.execute(
            'INSERT INTO adresse (person_id, strasse, postleitzahl, ort)'
            ' VALUES (?, ?, ?, ?)',
            (person_id, strasse, postleitzahl, ort)
        ).lastrowid
        dbcon.commit()

        kontaktartcode = 1 # fix für Telefon
        kontakt1 = request.form['kontakt1']
        if(len(kontakt1) > 0):
            bad_chars = [';', ':', '-', '/', ' ', '\n']
            kontakt_intern1 = ''.join(i for i in kontakt1 if not i in bad_chars)
            cursor.execute(
                'INSERT INTO kontakt (person_id, kontaktartcode, kontakt, kontakt_intern)'
                ' VALUES (?, ?, ?, ?)',
                (person_id, kontaktartcode, kontakt1, kontakt_intern1)
            )
            dbcon.commit()
        kontakt2 = request.form['kontakt2']
        if(len(kontakt2) > 0):
            bad_chars = [';', ':', '-', '/', ' ', '\n']
            kontakt_intern2 = ''.join(i for i in kontakt2 if not i in bad_chars)
            cursor.execute(
                'INSERT INTO kontakt (person_id, kontaktartcode, kontakt, kontakt_intern)'
                ' VALUES (?, ?, ?, ?)',
                (person_id, kontaktartcode, kontakt2, kontakt_intern2)
            )
            dbcon.commit()

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
        
        tier_id = cursor.execute(
            'INSERT INTO tier (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)
        ).lastrowid
        dbcon.commit()

        tierhaltung_id = cursor.execute(
            'INSERT INTO tierhaltung (person_id, tier_id)'
            ' VALUES (?, ?)',
            (person_id, tier_id)
        ).lastrowid
        dbcon.commit()
        cursor.close()
        return redirect(url_for('ordi.edit', id=tierhaltung_id))
    return render_template('ordi/create.html')


@bp.route('/<int:id>/edit', methods=('GET',))
@login_required
def edit(id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM tierhaltung, person, tier'
        ' WHERE tierhaltung.id = ? AND tierhaltung.person_id = person.id AND tierhaltung.tier_id = tier.id',
        (id,)
    )
    karteikarte = cursor.fetchone()
    person_id = karteikarte['person_id']

    cursor.execute(
        'SELECT * FROM adresse WHERE adresse.person_id = ?',
        (person_id,)
    )
    adresse = cursor.fetchone()

    cursor.execute(
        'SELECT * FROM kontakt WHERE kontakt.person_id = ?',
        (person_id,)
    )
    kontakte = cursor.fetchall()

    cursor.execute(
        'SELECT * FROM behandlung JOIN tierhaltung ON behandlung.tier_id = tierhaltung.tier_id'
        ' WHERE tierhaltung.id = ?',
        (id,)
    )
    behandlungen = cursor.fetchall()
    cursor.close()
    return render_template('ordi/edit.html', karteikarte=karteikarte, adresse=adresse, kontakte=kontakte, behandlungen=behandlungen)


@bp.route('/<int:person_id>/addtier', methods=('GET', 'POST'))
@login_required
def addtier(person_id):
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
        tier_id = cursor.execute(
            'INSERT INTO tier (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)
        ).lastrowid
        dbcon.commit()

        tierhaltung_id = cursor.execute(
            'INSERT INTO tierhaltung (person_id, tier_id)'
            ' VALUES (?, ?)',
            (person_id, tier_id)
        ).lastrowid
        dbcon.commit()
        cursor.close()
        return redirect(url_for('ordi.index'))
    return render_template('ordi/addtier.html')


@bp.route('/<int:tierhaltung_id>/newbehandlung', methods=('GET', 'POST'))
@login_required
def newbehandlung(tierhaltung_id):
    if(request.method == 'POST'):
        behandlungsdatum = request.form['behandlungsdatum']
        if(len(behandlungsdatum) == 0):
            behandlungsdatum = date.today().strftime("%Y-%m-%d")
        """good_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        behandlungsdatum = ''.join(i for i in request.form['behandlungsdatum'] if i in good_chars)
        if(len(behandlungsdatum) != 8):
            behandlungsdatum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            behandlungsdatum += datetime.now().strftime(" %H:%M:%S")"""
        gewicht_Kg = request.form['gewicht_Kg']
        diagnose = request.form['diagnose']
        laborwerte1 = request.form['laborwerte1']
        laborwerte2 = request.form['laborwerte2']
        arzneien = request.form['arzneien']
        arzneimittel = request.form['arzneimittel']
        impfungen_extern = request.form['impfungen_extern']

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute(
            'SELECT * FROM tierhaltung WHERE id = ?',
            (tierhaltung_id,)
        )
        tierhaltung = cursor.fetchone()

        cursor.execute(
            'INSERT INTO behandlung (tier_id, behandlungsdatum, gewicht_Kg, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (tierhaltung['tier_id'], behandlungsdatum, gewicht_Kg, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern)
        )
        dbcon.commit()
        cursor.close()
    return redirect(url_for('ordi.edit', id=tierhaltung['id']))


@bp.route('/<int:behandlung_id>/editbehandlung', methods=('GET', 'POST'))
@login_required
def editbehandlung(behandlung_id):
    if(request.method == 'POST'):
        behandlungsdatum = request.form['behandlungsdatum']
        """good_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        behandlungsdatum = ''.join(i for i in request.form['behandlungsdatum'] if i in good_chars)"""
        if(len(behandlungsdatum) == 0):
            behandlungsdatum = date.today().strftime("%Y-%m-%d")
        gewicht_Kg = request.form['gewicht_Kg']
        diagnose = request.form['diagnose']
        laborwerte1 = request.form['laborwerte1']
        laborwerte2 = request.form['laborwerte2']
        arzneien = request.form['arzneien']
        arzneimittel = request.form['arzneimittel']
        impfungen_extern = request.form['impfungen_extern']

        dbcon = get_db()
        cursor = dbcon.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute(
            'UPDATE behandlung SET behandlungsdatum = ?, gewicht_Kg = ?, diagnose = ?, laborwerte1 = ?, laborwerte2 = ?, arzneien = ?, arzneimittel = ?, impfungen_extern = ?'
            ' WHERE behandlung.id = ?',
            (behandlungsdatum, gewicht_Kg, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern, behandlung_id)
        )
        dbcon.commit()
        cursor.close()

    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT tierhaltung.id'
        ' FROM tierhaltung JOIN behandlung ON tierhaltung.tier_id = behandlung.tier_id'
        ' WHERE behandlung.id = ?',
        (behandlung_id,)
    )
    tierhaltung = cursor.fetchone()
    cursor.close()
    return redirect(url_for('ordi.edit', id=tierhaltung['id']))


@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('DELETE FROM tierhaltung WHERE id = ?', (id,))
    dbcon.commit()
    cursor.close()
    return redirect(url_for('ordi.index'))

