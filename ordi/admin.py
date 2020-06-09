

import os
from datetime import date, datetime
import random

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


def anonymize_token(data):
    new = ""
    for char in data:
        if(len(new) <= 2):
            new += char
        elif(ord(char) >= ord('0') and ord(char) <= ord('9')):
            rndnum = random.randint(0, 3)
            newnum = ord(char) + rndnum
            if(newnum >= ord('0') and newnum <= ord('9')):
                new += chr(newnum)
            else:
                new += '4'
        elif(ord(char) >= ord('A') and ord(char) <= ord('z')):
            rndnum = random.randint(0, 9)
            newnum = ord(char) + rndnum
            if(newnum >= ord('A') and newnum <= ord('z')):
                new += chr(newnum)
            else:
                new += 'g'
        else:
            new += char
    return new


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
                    if(quotecnt % 2 == 0):
                        fo2.write(char)
                        cnt += 1
                    else:
                        fo2.write(',')
                    continue
                elif(char == '\n'):
                    if(quotecnt % 2 == 1 or cnt % rowcnt != 0):
                        fo2.write('§')
                    else:
                        fo2.write(char)
                    continue
                else:
                    fo2.write(char)
    return path_and_filename2


def anonymize_file(filename, rowcnt, indices):
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw', filename)

    path_and_filename2 = clean_file(path_and_filename, rowcnt - 1)

    path_and_filenameX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', filename)

    with open(path_and_filename2) as fo2:
        with open(path_and_filenameX, "w") as foX:
            for line in fo2:
                line = line.replace('§', '\n')
                arrline = line.split(";")

                if(len(arrline) != rowcnt):
                    print("error", end=" ", flush=True)
                    print(arrline, end="", flush=True)
                    continue

                for idx in range(len(arrline)):
                    found = False
                    for idx2 in indices:
                        if(idx == idx2):
                            #token = arrline[idx].strip('"')
                            #if(len(token) > 0):
                            foX.write(anonymize_token(arrline[idx]))
                            found = True
                            break
                    if(found == False):
                        foX.write(arrline[idx])
                    if(idx < rowcnt - 1):
                        foX.write(";")

    os.remove(path_and_filename2)


def import_tier():
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', "tblTier.txt")

    path_and_filename2 = clean_file(path_and_filename, 11)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 12):
                print(arrline[0], end="", flush=True)
                continue

            try:
                tier = Tier()

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

                if(arrline[11].strip('\n') == "1"):
                    tier.patient = True
                else:
                    tier.patient = False

                db.session.add(tier)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            tier = db.session.execute("SELECT id FROM tier ORDER BY Id DESC LIMIT 1").fetchone()
            db.session.execute("ALTER SEQUENCE tier_id_seq RESTART WITH " + str(tier['id'] + 1))
            return True
        except Exception as err:
            print(err)
            return False
    else:
        db.session.rollback()
        return False


def import_person(person_id):
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', "tblPerson.txt")

    path_and_filename2 = clean_file(path_and_filename, 6)

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 7):
                print(arrline[0], end="", flush=True)
                continue

            try:
                p_id = int(arrline[0])

                if(p_id < person_id):
                    continue

                person = Person()

                person.id = p_id

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

                if(arrline[6].strip('\n') == "1"):
                    person.kunde = True
                else:
                    person.kunde = False

                db.session.add(person)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            person = db.session.execute("SELECT id FROM person ORDER BY Id DESC LIMIT 1").fetchone()
            db.session.execute("ALTER SEQUENCE person_id_seq RESTART WITH " + str(person['id'] + 1))
            return True
        except Exception as err:
            print(err)
            return False
    else:
        db.session.rollback()
        return False


def import_adresse():
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', "tblAdresse.txt")

    path_and_filename2 = clean_file(path_and_filename, 4)

    personen = db.session.query(Person).all()

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")
    
            if(len(arrline) != 5):
                print(arrline[0], end="", flush=True)
                continue

            try:
                p_id = int(arrline[0])

                for person in personen:
                    if(person.id == p_id):
                        person.adr_strasse = arrline[2].strip('"')
                        person.adr_plz = arrline[3].strip('"')
                        person.adr_ort = arrline[4].strip('"\n')
                        break
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
        except Exception as err:
            print(err)
            return False
    else:
        db.session.rollback()
        return False


def import_kontakt():
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', "tblKontakt.txt")

    path_and_filename2 = clean_file(path_and_filename, 4)

    personen = db.session.query(Person).all()

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
                p_id = int(arrline[0])

                for person in personen:
                    if(person.id == p_id):
                        if(person.kontakte and len(person.kontakte) > 0):
                            person.kontakte += " " + arrline[3].strip('"\n')
                        else:
                            person.kontakte = arrline[3].strip('"\n')
                    break
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
        except Exception as err:
            print(err)
            return False
    else:
        db.session.rollback()
        return False


def import_tierhaltung():
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', "tblTierhaltung.txt")

    path_and_filename2 = clean_file(path_and_filename, 2)

    personen = db.session.query(Person).all()

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 3):
                print(arrline[0], end="", flush=True)
                continue

            try:
                person_id = int(arrline[0])

                tier_id = int(arrline[1])

                found = False

                for person in personen:
                    if(person.id == person_id):
                        found = True
                        break
                if(found == False):
                    db.session.delete(tier_id)
                    continue

                tierhaltung = Tierhaltung()

                tierhaltung.person_id = person_id

                tierhaltung.tier_id = tier_id

                tierhaltung.created_at = datetime.strptime((arrline[2])[:10], "%Y-%m-%d")

                db.session.add(tierhaltung)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            tierhaltung = db.session.execute("SELECT id FROM tierhaltung ORDER BY Id DESC LIMIT 1").fetchone()
            db.session.execute("ALTER SEQUENCE tierhaltung_id_seq RESTART WITH " + str(tierhaltung['id'] + 1))
            return True
        except Exception as err:
            print(err)
            return False
    else:
        db.session.rollback()
        return False


def import_behandlung():
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', "tblBehandlung.txt")

    path_and_filename2 = clean_file(path_and_filename, 9)

    tierhaltungen = db.session.query(Tierhaltung).all()

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 10):
                print(arrline[0], end="", flush=True)
                continue

            try:
                tier_id = int(arrline[0])

                found = False

                for tierhaltung in tierhaltungen:
                    if(tierhaltung.tier_id == tier_id):
                        found = True
                        break
                if(found == False):
                    continue

                behandlung = Behandlung()

                behandlung.id = int(arrline[1])

                behandlung.tier_id = tier_id

                if(len(arrline[2]) > 0):
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
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break
    
    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            behandlung = db.session.execute("SELECT id FROM behandlung ORDER BY Id DESC LIMIT 1").fetchone()
            db.session.execute("ALTER SEQUENCE behandlung_id_seq RESTART WITH " + str(behandlung['id'] + 1))
            return True
        except Exception as err:
            print(err)
            return False
    else:
        db.session.rollback()
        return False


def import_impfung():
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', "tblImpfung.txt")

    path_and_filename2 = clean_file(path_and_filename, 1)

    behandlungen = db.session.query(Behandlung).all()

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 2):
                print(arrline[0], end="", flush=True)
                continue

            try:
                behandlung_id = int(arrline[0])

                found = False

                for behandlung in behandlungen:
                    if(behandlung.id == behandlung_id):
                        found = True
                        break
                if(found == False):
                    continue

                impfung = Impfung()

                impfung.behandlung_id = behandlung_id

                impfung.impfungscode = int(arrline[1])

                db.session.add(impfung)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break

    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            #impfung = db.session.execute("SELECT id FROM impfung ORDER BY Id DESC LIMIT 1").fetchone()
            #db.session.execute("ALTER SEQUENCE impfung_id_seq RESTART WITH " + str(impfung['id'] + 1))
            return True
        except Exception as err:
            print(err)
            return False
    else:
        db.session.rollback()
        return False


def import_behandlungsverlauf():
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', "tblBehandlungsverlauf.txt")

    path_and_filename2 = clean_file(path_and_filename, 5)

    tierhaltungen = db.session.query(Tierhaltung).all()

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 6):
                print(str(len(arrline)) + " " + line, end="", flush=True)
                continue

            try:
                person_id = int(arrline[1])

                tier_id = int(arrline[2])

                found = False

                for tierhaltung in tierhaltungen:
                    if(tierhaltung.person_id == person_id and 
                       tierhaltung.tier_id == tier_id):
                        found = True
                        break
                if(found == False):
                    continue

                behandlungsverlauf = Behandlungsverlauf()

                #behandlungsverlauf.id = int(arrline[0])

                behandlungsverlauf.person_id = person_id

                behandlungsverlauf.tier_id = tier_id

                if(len(arrline[3]) > 0):
                    behandlungsverlauf.datum = datetime.strptime((arrline[3])[:10], "%Y-%m-%d")
                else:
                    behandlungsverlauf.datum = date(year=1900, month=1, day=1)

                behandlungsverlauf.diagnose = arrline[4].strip('"')

                behandlungsverlauf.behandlung = arrline[5].strip('"\n')

                db.session.add(behandlungsverlauf)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break
    
    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            #behandlungsverlauf = db.session.execute("SELECT id FROM behandlungsverlauf ORDER BY Id DESC LIMIT 1").fetchone()
            #db.session.execute("ALTER SEQUENCE behandlungsverlauf_id_seq RESTART WITH " + str(behandlungsverlauf['id'] + 1))
            return True
        except Exception as err:
            print(err)
            return False
    else:
        db.session.rollback()
        return False


def import_rechnung():
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', "tblRechnung.txt")

    path_and_filename2 = clean_file(path_and_filename, 13)

    tierhaltungen = db.session.query(Tierhaltung).all()

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 14):
                print(arrline[0], end="", flush=True)
                continue

            try:
                person_id = int(arrline[1])

                tier_id = int(arrline[2])

                found = False

                for tierhaltung in tierhaltungen:
                    if(tierhaltung.person_id == person_id and 
                       tierhaltung.tier_id == tier_id):
                        found = True
                        break
                if(found == False):
                    continue

                rechnung = Rechnung()

                rechnung.id = int(arrline[0])

                rechnung.person_id = person_id

                rechnung.tier_id = tier_id

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
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break
    
    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            rechnung = db.session.execute("SELECT id FROM rechnung ORDER BY Id DESC LIMIT 1").fetchone()
            db.session.execute("ALTER SEQUENCE rechnung_id_seq RESTART WITH " + str(rechnung['id'] + 1))
            return True
        except Exception as err:
            print(err)
            return False
    else:
        db.session.rollback()
        return False


def import_rechnungszeile():
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', "tblRechnungszeile.txt")

    path_and_filename2 = clean_file(path_and_filename, 5)

    rechnungen = db.session.query(Rechnung).all()

    ok = True

    with open(path_and_filename2) as fo:
        for line in fo:
            line = line.replace('§', '\n')
            arrline = line.split(";")

            if(len(arrline) != 6):
                print(arrline[0], end="", flush=True)
                continue

            try:
                rechnung_id = int(arrline[1])

                found = False

                for rechnung in rechnungen:
                    if(rechnung.id == rechnung_id):
                        found = True
                        break
                if(found == False):
                    continue

                rechnungszeile = Rechnungszeile()

                #rechnungszeile.id = int(arrline[0])

                rechnungszeile.rechnung_id = rechnung_id

                rechnungszeile.artikelcode = int(arrline[2])

                if(len(arrline[3]) > 0):
                    rechnungszeile.datum = datetime.strptime((arrline[3])[:10], "%Y-%m-%d")
                else:
                    rechnungszeile.datum = date(year=1900, month=1, day=1)

                rechnungszeile.artikel = arrline[4].strip('"')

                rechnungszeile.betrag = float(arrline[5].replace(',', '.'))

                db.session.add(rechnungszeile)
            except:
                ok = False
                print("error", end=" ", flush=True)
                print(arrline, flush=True)
                break
    
    os.remove(path_and_filename2)

    if(ok):
        try:
            db.session.commit()
            #rechnungszeile = db.session.execute("SELECT id FROM rechnungszeile ORDER BY Id DESC LIMIT 1").fetchone()
            #db.session.execute("ALTER SEQUENCE rechnungszeile_id_seq RESTART WITH " + str(rechnungszeile['id'] + 1))
            return True
        except Exception as err:
            print(err)
            return False
    else:
        db.session.rollback()
        return False


@bp.route('/<int:phase>/dbwrite', methods=('GET',))
@login_required
def dbwrite(phase):
    if(phase == 1):
        print("starte tier import")
        dbwrite_ok = import_tier()
        if(dbwrite_ok == False):
            return redirect(url_for('admin.index', dbwrite_ok=dbwrite_ok))

        print("starte person import")
        dbwrite_ok = import_person(5000)
        if(dbwrite_ok == False):
            return redirect(url_for('admin.index', dbwrite_ok=dbwrite_ok))

        print("starte adresse import")
        dbwrite_ok = import_adresse()
        if(dbwrite_ok == False):
            return redirect(url_for('admin.index', dbwrite_ok=dbwrite_ok))

        print("starte kontakt import")
        dbwrite_ok = import_kontakt()
        if(dbwrite_ok == False):
            return redirect(url_for('admin.index', dbwrite_ok=dbwrite_ok))

    if(phase == 2):
        print("starte tierhaltung import")
        dbwrite_ok = import_tierhaltung()
        if(dbwrite_ok == False):
            return redirect(url_for('admin.index', dbwrite_ok=dbwrite_ok))

    if(phase == 3):
        print("starte behandlung import")
        dbwrite_ok = import_behandlung()
        if(dbwrite_ok == False):
            return redirect(url_for('admin.index', dbwrite_ok=dbwrite_ok))

        print("starte impfung import")
        dbwrite_ok = import_impfung()
        if(dbwrite_ok == False):
            return redirect(url_for('admin.index', dbwrite_ok=dbwrite_ok))

    if(phase == 4):
        print("starte behandlungsverlauf import")
        dbwrite_ok = import_behandlungsverlauf()
        if(dbwrite_ok == False):
            return redirect(url_for('admin.index', dbwrite_ok=dbwrite_ok))

        print("starte rechnung import")
        dbwrite_ok = import_rechnung()
        if(dbwrite_ok == False):
            return redirect(url_for('admin.index', dbwrite_ok=dbwrite_ok))

        print("starte rechnungszeile import")
        dbwrite_ok = import_rechnungszeile()
        if(dbwrite_ok == False):
            return redirect(url_for('admin.index', dbwrite_ok=dbwrite_ok))

    return redirect(url_for('admin.index', dbwrite_ok=True))


@bp.route('/anonymize', methods=('GET',))
@login_required
def anonymize():
    anonymize_file("tblTier.txt", 12, [1, 5, 6])

    anonymize_file("tblPerson.txt", 7, [3, 4, 5])

    anonymize_file("tblAdresse.txt", 5, [2, 3, 4])

    anonymize_file("tblKontakt.txt", 5, [3])

    anonymize_file("tblTierhaltung.txt", 3, [])

    anonymize_file("tblBehandlung.txt", 10, [4])

    anonymize_file("tblImpfung.txt", 2, [])

    anonymize_file("tblBehandlungsverlauf.txt", 6, [4, 5])

    anonymize_file("tblRechnung.txt", 14, [7])

    anonymize_file("tblRechnungszeile.txt", 6, [])

    return redirect(url_for('admin.index', dbwrite_ok=False))
