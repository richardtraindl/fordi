

import os
from datetime import date, datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from . import db
from sqlalchemy import or_, and_
from ordi.auth import login_required
from ordi.models import Termin, Tierhaltung, Person, Tier

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    return render_template('admin/admin.html', page_title="Admin")


@bp.route('/database', methods=('GET', 'POST'))
@login_required
def database():
    return render_template('admin/database.html', page_title="Database")


def clean(line):
    newline = ""
    cnt = 0
    for char in line:
        if(char == '"'):
            cnt += 1
            newline += char
        elif(char == ';' and cnt % 2 == 1):
            newline += ","
            continue
        else:
            newline += char
    return newline

def import_tier():
    filename = "tblTier.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)
    with open(path_and_filename) as openfileobject:
        ok = True
        for line in openfileobject:
            cleanline = clean(line)
            arrline = cleanline.split(";")

            if(len(arrline) != 12):
                print(arrline[0], end="", flush=True)
                continue

            tier = Tier()

            try:            
                tier.id = int(arrline[0])

                if(len(arrline[1]) > 0):
                    tier.tiername = arrline[1].strip('"')
                else:
                    tier.tiername = "__unbekannt__"

                tier.tierart = arrline[2].strip('"')

                tier.rasse = arrline[3].strip('"')

                tier.farbe = arrline[4].strip('"')

                tier.viren = arrline[5].strip('"')

                tier.merkmal = arrline[6].strip('"')

                if(len(arrline[7]) > 0):
                    tier.geburtsdatum = datetime.strptime((arrline[7])[:10], "%Y-%m-%d")
                else:
                    tier.geburtsdatum = date(year=1900, month=1, day=1)

                if(len(arrline[8]) > 0):
                    tier.geschlechtscode = int(arrline[8])
                else:
                    tier.geschlechtscode = 0

                tier.chip_nummer = arrline[9].strip('"')

                tier.eu_passnummer = arrline[10].strip('"')

                tier.patient = int(arrline[11].strip('\n'))

                db.session.add(tier)
                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

        if(ok):
            db.session.commit()
            return True
        else:
            db.session.rollback()
            return False

def import_person():
    filename = "tblPerson.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)
    with open(path_and_filename) as openfileobject:
        ok = True
        for line in openfileobject:
            cleanline = clean(line)
            arrline = cleanline.split(";")

            if(len(arrline) != 7):
                print(arrline[0], end="", flush=True)
                continue

            person = Person()

            try:            
                person.id = int(arrline[0])

                if(len(arrline[1]) > 0):
                    person.anredecode = int(arrline[1])
                else:
                    person.anredecode = 0

                person.titel = arrline[2].strip('"')

                if(len(arrline[3]) > 0):
                    person.familienname = arrline[3].strip('"')
                else:
                    person.familienname = "__unbekannt__"

                person.vorname = arrline[4].strip('"')

                person.notiz = arrline[5].strip('"')

                person.kunde = int(arrline[6].strip('\n'))

                db.session.add(person)
                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

        if(ok):
            db.session.commit()
            return True
        else:
            db.session.rollback()
            return False

def import_adresse():
    filename = "tblAdresse.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)
    with open(path_and_filename) as openfileobject:
        ok = True
        for line in openfileobject:
            cleanline = clean(line)
            arrline = cleanline.split(";")
            
            if(len(arrline) != 5):
                print(arrline[0], end="", flush=True)
                continue

            try:
                person_id = int(arrline[1])
                person = db.session.query(Person).get(person_id)

                person.adr_strasse = arrline[2].strip('"')

                person.adr_plz = arrline[3].strip('"')
                
                person.adr_ort = arrline[4].strip('"')

                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

        if(ok):
            db.session.commit()
            return True
        else:
            db.session.rollback()
            return False

def import_kontakt():
    filename = "tblKontakt.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)
    ok = True
    with open(path_and_filename) as openfileobject:
        for line in openfileobject:
            cleanline = clean(line)
            arrline = cleanline.split(";")

            if(len(arrline) != 5):
                print(arrline[0], end="", flush=True)
                continue

            if(len(arrline[3]) == 0):
                continue

            try:
                person_id = int(arrline[1])
                person = db.session.query(Person).get(person_id)

                if(person.kontakte and len(person.kontakte) > 0):
                    person.kontakte += " " + arrline[3].strip('"')
                else:
                    person.kontakte = arrline[3].strip('"')                    

                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(str(person.id), flush=True)
                break

    if(ok):
        db.session.commit()
        return True
    else:
        db.session.rollback()
        return False

def import_tierhaltung():
    filename = "tblTierhaltung.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)
    with open(path_and_filename) as openfileobject:
        ok = True
        for line in openfileobject:
            cleanline = clean(line)
            arrline = cleanline.split(";")

            if(len(arrline) != 4):
                print(arrline[0], end="", flush=True)
                continue

            tierhaltung = Tierhaltung()

            try:            
                tierhaltung.id = int(arrline[0])
                
                tierhaltung.person_id = int(arrline[1])
                
                tierhaltung.tier_id = int(arrline[2])
                
                tierhaltung.anlagezeit = datetime.strptime((arrline[3])[:10], "%Y-%m-%d")

                db.session.add(tierhaltung)
                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

        if(ok):
            db.session.commit()
            return True
        else:
            db.session.rollback()
            return False

@bp.route('/write', methods=('GET', 'POST'))
@login_required
def write():
    if(import_tier() == False):
        return render_template('admin/database.html', ok=False, page_title="Database")

    if(import_person() == False):
        return render_template('admin/database.html', ok=False, page_title="Database")
    
    if(import_adresse() == False):
        return render_template('admin/database.html', ok=False, page_title="Database")

    if(import_kontakt() == False):
        return render_template('admin/database.html', ok=False, page_title="Database")

    if(import_tierhaltung() == False):
        return render_template('admin/database.html', ok=False, page_title="Database")

    return render_template('admin/database.html', ok=True, page_title="Database")

