

import os
from datetime import date, datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from . import db
from sqlalchemy import or_, and_
from ordi.auth import login_required
from ordi.models import *
from ordi.values import *
from ordi.util.helper import *

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    dbwrite_ok = request.args.get('dbwrite_ok')
    return render_template('admin/index.html', dbwrite_ok=dbwrite_ok, page_title="Admin")


def clean_file(path_and_filename, rowcnt):
    path_and_filename2 = path_and_filename + "2"
    with open(path_and_filename, "r") as fo:
        with open(path_and_filename2, "w") as fo2:
            cnt = 0
            quotecnt = 0
            for char in fo.read():
                if(char == '"'):
                    quotecnt += 1
                    fo2.write(char)
                    continue
                elif(char == ';'):
                    if(quotecnt % 2 == 1):
                        fo2.write(',')
                    else:
                        fo2.write(char)
                        cnt += 1
                    continue
                elif(char == '\n'):
                    if(cnt % rowcnt != 0):
                        fo2.write('§')
                    else:
                        fo2.write(char)                  
                    continue
                else:
                    fo2.write(char)
    return path_and_filename2


def import_tier():
    filename = "tblTier.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    path_and_filename2 = clean_file(path_and_filename, 11)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

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

    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        db.session.rollback()
        return False


def import_person():
    filename = "tblPerson.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    path_and_filename2 = clean_file(path_and_filename, 6)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

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

    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        db.session.rollback()
        return False


def import_adresse():
    filename = "tblAdresse.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    path_and_filename2 = clean_file(path_and_filename, 4)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")
    
            if(len(arrline) != 5):
                print(arrline[0], end="", flush=True)
                continue

            try:
                person_id = int(arrline[0])
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

    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        db.session.rollback()
        return False


def import_kontakt():
    filename = "tblKontakt.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    path_and_filename2 = clean_file(path_and_filename, 4)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 5):
                print(arrline[0], end="", flush=True)
                continue

            if(len(arrline[3]) == 0):
                continue

            try:
                person_id = int(arrline[0])
                person = db.session.query(Person).get(person_id)

                if(person.kontakte and len(person.kontakte) > 0):
                    person.kontakte += " " + arrline[3].strip('"')
                else:
                    person.kontakte = arrline[3].strip('"')

                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        db.session.rollback()
        return False


def import_tierhaltung():
    filename = "tblTierhaltung.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    path_and_filename2 = clean_file(path_and_filename, 2)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 3):
                print(arrline[0], end="", flush=True)
                continue

            tierhaltung = Tierhaltung()
            try:            
                tierhaltung.person_id = int(arrline[0])

                tierhaltung.tier_id = int(arrline[1])

                tierhaltung.created_at = datetime.strptime((arrline[2])[:10], "%Y-%m-%d")

                db.session.add(tierhaltung)
                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        db.session.rollback()
        return False


def import_behandlung():
    filename = "tblBehandlung.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    path_and_filename2 = clean_file(path_and_filename, 9)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 10):
                print(arrline[0], end="", flush=True)
                continue

            behandlung = Behandlung()
            try:
                behandlung.id = int(arrline[1])

                behandlung.tier_id = int(arrline[0])

                if(len(arrline[7]) > 0):
                    behandlung.datum = datetime.strptime((arrline[2])[:10], "%Y-%m-%d")
                else:
                    behandlung.datum = date(year=1900, month=1, day=1)

                behandlung.gewicht = arrline[3].strip('"')

                behandlung.diagnose = arrline[4].strip('"')

                behandlung.laborwerte1 = arrline[5].strip('"')

                behandlung.laborwerte2 = arrline[6].strip('"')

                behandlung.arzneien = arrline[7].strip('"')

                behandlung.arzneimittel = arrline[8].strip('"')

                db.session.add(behandlung)
                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break
    
    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        db.session.rollback()
        return False


def import_impfung():
    filename = "tblImpfung.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    path_and_filename2 = clean_file(path_and_filename, 1)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 2):
                print(arrline[0], end="", flush=True)
                continue

            impfung = Impfung()
            try:
                impfung.behandlung_id = int(arrline[0])

                impfung.impfungscode = int(arrline[1])

                db.session.add(impfung)
                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        db.session.rollback()
        return False


def import_behandlungsverlauf():
    filename = "tblBehandlungsverlauf.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    path_and_filename2 = clean_file(path_and_filename, 5)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 6):
                print(arrline[0], end="", flush=True)
                continue

            behandlungsverlauf = Behandlungsverlauf()
            try:
                behandlungsverlauf.id = int(arrline[0])

                behandlungsverlauf.person_id = int(arrline[1])

                behandlungsverlauf.tier_id = int(arrline[2])

                if(len(arrline[3]) > 0):
                    behandlungsverlauf.datum = datetime.strptime((arrline[3])[:10], "%Y-%m-%d")
                else:
                    behandlungsverlauf.datum = date(year=1900, month=1, day=1)

                behandlungsverlauf.diagnose = arrline[4].strip('"')

                behandlungsverlauf.behandlung = arrline[5].strip('"')

                db.session.add(behandlungsverlauf)
                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break
    
    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        db.session.rollback()
        return False


def import_rechnung():
    filename = "tblRechnung.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    path_and_filename2 = clean_file(path_and_filename, 13)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 14):
                print(arrline[0], end="", flush=True)
                continue

            rechnung = Rechnung()
            try:
                rechnung.id = int(arrline[0])

                rechnung.person_id = int(arrline[1])

                rechnung.tier_id = int(arrline[2])

                if(len(arrline[3]) > 0):
                    rechnung.jahr = int(arrline[3])
                else:
                    rechnung.jahr = 1900

                if(len(arrline[4]) > 0):
                    rechnung.lfnr = int(arrline[4])
                else:
                    rechnung.lfnr = 0

                if(len(arrline[5]) > 0):
                    rechnung.datum = datetime.strptime((arrline[5])[:10], "%Y-%m-%d")
                else:
                    rechnung.datum = date(year=1900, month=1, day=1)

                rechnung.ort = arrline[6].strip('"')

                rechnung.diagnose = arrline[7].strip('"')

                rechnung.bezahlung = arrline[8].strip('"')

                rechnung.brutto_summe = float(arrline[9].replace(',','.'))

                rechnung.netto_summe = float(arrline[10].replace(',','.'))

                rechnung.steuerbetrag_zwanzig = float(arrline[11].replace(',','.'))

                rechnung.steuerbetrag_dreizehn = float(arrline[12].replace(',','.'))

                rechnung.steuerbetrag_zehn = float(arrline[13].replace(',','.'))

                db.session.add(rechnung)
                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break
    
    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        db.session.rollback()
        return False


def import_rechnungszeile():
    filename = "tblRechnungszeile.txt"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    path_and_filename2 = clean_file(path_and_filename, 5)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 6):
                print(arrline[0], end="", flush=True)
                continue

            rechnungszeile = Rechnungszeile()
            try:
                rechnungszeile.id = int(arrline[0])

                rechnungszeile.rechnung_id = int(arrline[1])

                rechnungszeile.artikelcode = int(arrline[2])

                if(len(arrline[3]) > 0):
                    rechnungszeile.datum = datetime.strptime((arrline[3])[:10], "%Y-%m-%d")
                else:
                    rechnungszeile.datum = date(year=1900, month=1, day=1)

                rechnungszeile.artikel = arrline[4].strip('"')

                rechnungszeile.betrag = float(arrline[5].replace(',', '.'))

                db.session.add(rechnungszeile)
                print(".", end="", flush=True)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break
    
    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        db.session.rollback()
        return False


@bp.route('/dbwrite', methods=('GET',))
@login_required
def dbwrite():
    if(import_tier() == False):
        return redirect(url_for('admin.index', dbwrite_ok=False))

    if(import_person() == False):
        return redirect(url_for('admin.index', dbwrite_ok=False))
    
    if(import_adresse() == False):
        return redirect(url_for('admin.index', dbwrite_ok=False))

    if(import_kontakt() == False):
        return redirect(url_for('admin.index', dbwrite_ok=False))

    if(import_tierhaltung() == False):
        return redirect(url_for('admin.index', dbwrite_ok=False))

    if(import_behandlung() == False):
        return redirect(url_for('admin.index', dbwrite_ok=False))

    if(import_impfung() == False):
        return redirect(url_for('admin.index', dbwrite_ok=False))

    if(import_behandlungsverlauf() == False):
        return redirect(url_for('admin.index', dbwrite_ok=False))

    if(import_rechnung() == False):
        return redirect(url_for('admin.index', dbwrite_ok=False))

    if(import_rechnungszeile() == False):
        return redirect(url_for('admin.index', dbwrite_ok=False))

    return redirect(url_for('admin.index', dbwrite_ok=True))

