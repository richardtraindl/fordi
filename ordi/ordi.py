

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
    cur = dbcon.cursor()
    cur.execute(
        'SELECT * FROM tierhaltung, person, tier WHERE tierhaltung.person_id = person.id AND tierhaltung.tier_id = tier.id'
        ' ORDER BY familienname ASC'
    )
    tierhaltungen = cur.fetchall()
    return render_template('ordi/index.html', tierhaltungen=tierhaltungen)


@bp.route('/<int:id>/karteikarte', methods=('GET',))
@login_required
def karteikarte(id):
    dbcon = get_db()
    cur = dbcon.cursor()
    cur.execute(
        'SELECT * FROM tierhaltung, person, adresse, kontakt, tier'
        ' WHERE tierhaltung.id = ? AND tierhaltung.person_id = person.id AND tierhaltung.tier_id = tier.id'
        ' AND tierhaltung.person_id = adresse.person_id AND tierhaltung.person_id = kontakt.person_id',
        (id,)
    )
    karteikarte = cur.fetchone()

    cur.execute(
        'SELECT * FROM tierhaltung, behandlung'
        ' WHERE tierhaltung.id = ? AND tierhaltung.tier_id = behandlung.tier_id ORDER BY behandlungsdatum DESC',
        (id,)
    )
    behandlungen = cur.fetchall()
    print(id, behandlungen)
    cur.close()
    return render_template('ordi/karteikarte.html', karteikarte=karteikarte, behandlungen=behandlungen)


@bp.route('/newtierhaltung', methods=('GET', 'POST'))
@login_required
def newkarteikarte():
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
        dbcon.execute('pragma foreign_keys=ON')
        cur = dbcon.cursor()
        person_id = cur.execute(
            'INSERT INTO person (anredeartcode, titel, familienname, vorname, notiz, kunde)'
            ' VALUES (?, ?, ?, ?, ?, ?)',
            (anredeartcode, titel, familienname, vorname, notiz, kunde)
        ).lastrowid
        dbcon.commit()

        strasse = request.form['strasse']
        postleitzahl = request.form['postleitzahl']
        ort = request.form['ort']
        adresse_id = cur.execute(
            'INSERT INTO adresse (person_id, strasse, postleitzahl, ort)'
            ' VALUES (?, ?, ?, ?)',
            (person_id, strasse, postleitzahl, ort)
        ).lastrowid
        dbcon.commit()

        kontaktartcode = request.form['kontaktartcode']
        kontakt = request.form['kontakt']
        bad_chars = [';', ':', '-', '/', ' ', '\n']
        kontakt_intern = ''.join(i for i in kontakt if not i in bad_chars)
        kontakt_id = cur.execute(
            'INSERT INTO kontakt (person_id, kontaktartcode, kontakt, kontakt_intern)'
            ' VALUES (?, ?, ?, ?)',
            (person_id, kontaktartcode, kontakt, kontakt_intern)
        ).lastrowid
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
        
        tier_id = cur.execute(
            'INSERT INTO tier (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)
        ).lastrowid
        dbcon.commit()

        tierhaltung_id = cur.execute(
            'INSERT INTO tierhaltung (person_id, tier_id)'
            ' VALUES (?, ?)',
            (person_id, tier_id)
        ).lastrowid
        dbcon.commit()
        cur.close()
        return redirect(url_for('ordi.index'))
    return render_template('ordi/newkarteikarte.html')


@bp.route('/newperson', methods=('GET', 'POST'))
@login_required
def newperson():
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
        dbcon.execute('pragma foreign_keys=ON')
        cur = dbcon.cursor()
        cur.execute(
            'INSERT INTO person (anredeartcode, titel, familienname, vorname, notiz, kunde)'
            ' VALUES (?, ?, ?, ?, ?, ?)',
            (anredeartcode, titel, familienname, vorname, notiz, kunde)
        )
        dbcon.commit()
        cur.close()
        return redirect(url_for('ordi.index'))
    return render_template('ordi/person.html')


@bp.route('/newtier', methods=('GET', 'POST'))
@login_required
def newtier():
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
        dbcon.execute('pragma foreign_keys=ON')
        cur = dbcon.cursor()
        tier_id = cur.execute(
            'INSERT INTO tier (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)
        ).lastrowid
        dbcon.commit()

        cur.close()
        return redirect(url_for('ordi.index'))
    return render_template('ordi/tier.html')


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
        dbcon.execute('pragma foreign_keys=ON')
        cur = dbcon.cursor()
        tier_id = cur.execute(
            'INSERT INTO tier (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)
        ).lastrowid
        dbcon.commit()

        tierhaltung_id = cur.execute(
            'INSERT INTO tierhaltung (person_id, tier_id)'
            ' VALUES (?, ?)',
            (person_id, tier_id)
        ).lastrowid
        dbcon.commit()
        cur.close()
        return redirect(url_for('ordi.index'))
    return render_template('ordi/addtier.html')


@bp.route('/<int:tierhaltung_id>/newbehandlung', methods=('GET', 'POST'))
@login_required
def newbehandlung(tierhaltung_id):
    if(request.method == 'POST'):
        behandlungsdatum = request.form['behandlungsdatum']
        gewicht_Kg = request.form['gewicht_Kg']
        diagnose = request.form['diagnose']
        laborwerte1 = request.form['laborwerte1']
        laborwerte2 = request.form['laborwerte2']
        arzneien = request.form['arzneien']
        arzneimittel = request.form['arzneimittel']
        impfungen_extern = request.form['impfungen_extern']

        dbcon = get_db()
        dbcon.execute('pragma foreign_keys=ON')
        cur = dbcon.cursor()
        cur.execute(
            'SELECT * FROM tierhaltung WHERE id = ?',
            (tierhaltung_id,)
        )
        tierhaltung = cur.fetchone()

        cur.execute(
            'INSERT INTO behandlung (tier_id, behandlungsdatum, gewicht_Kg, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (tierhaltung['tier_id'], behandlungsdatum, gewicht_Kg, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern)
        )
        dbcon.commit()
        cur.close()
    return redirect(url_for('ordi.karteikarte', id=tierhaltung['id']))


@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id):
    dbcon = get_db()
    dbcon.execute('pragma foreign_keys=ON')
    cur = dbcon.cursor()
    cur.execute('DELETE FROM tierhaltung WHERE id = ?', (id,))
    dbcon.commit()
    cur.close()
    return redirect(url_for('ordi.index'))

