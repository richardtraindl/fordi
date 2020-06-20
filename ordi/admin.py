

import os, io
from datetime import date, datetime
import gdown

from flask import Flask, Blueprint, flash, g, redirect, render_template, request, url_for
import click

from . import db
from ordi.auth import admin_login_required
from ordi.models import *


bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def index(filename=None):
    return render_template('admin/index.html', page_title="Admin")


@bp.cli.command("import-tier")
@click.argument("url")
def import_tier(url):
    filename = 'tblTier.txt'
    gdown.download(url, filename, quiet=False) 
    import_tier(filename)
    os.remove(filename)


@bp.cli.command("import-person")
@click.argument("url")
def import_person(url):
    filename = 'tblPerson.txt'
    gdown.download(url, filename, quiet=False) 
    import_person(filename)
    os.remove(filename)


@bp.cli.command("import-adresse")
@click.argument("url")
def import_adresse(url):
    filename = 'tblAdresse.txt'
    gdown.download(url, filename, quiet=False) 
    import_adresse(filename)
    os.remove(filename)


@bp.cli.command("import-kontakt")
@click.argument("url")
def import_kontakt(url):
    filename = 'tblKontakt.txt'
    gdown.download(url, filename, quiet=False) 
    import_kontakt(filename)
    os.remove(filename)


@bp.cli.command("import-tierhaltung")
@click.argument("url")
def import_tierhaltung(url):
    filename = 'tblTierhaltung.txt'
    gdown.download(url, filename, quiet=False) 
    import_tierhaltung(filename)
    os.remove(filename)


@bp.cli.command("import-behandlung")
@click.argument("url")
def import_behandlung(url):
    filename = 'tblBehandlung.txt'
    gdown.download(url, filename, quiet=False) 
    import_behandlung(filename)
    os.remove(filename)


@bp.cli.command("import-impfung")
@click.argument("url")
def import_impfung(url):
    filename = 'tblImpfung.txt'
    gdown.download(url, filename, quiet=False) 
    import_impfung(filename)
    os.remove(filename)


@bp.cli.command("import-behandlungsverlauf")
@click.argument("url")
def import_behandlungsverlauf(url):
    filename = 'tblBehandlungsverlauf.txt'
    gdown.download(url, filename, quiet=False) 
    import_behandlungsverlauf(filename)
    os.remove(filename)


@bp.cli.command("import-rechnung")
@click.argument("url")
def import_rechnung(url):
    filename = 'tblRechnung.txt'
    gdown.download(url, filename, quiet=False) 
    import_rechnung(filename)
    os.remove(filename)

@bp.cli.command("import-rechnungszeile")
@click.argument("url")
def import_rechnungszeile(url):
    filename = 'tblRechnungszeile.txt'
    gdown.download(url, filename, quiet=False) 
    import_rechnungszeile(filename)
    os.remove(filename)


def clean_str_file(str_file, rowcnt):
    new = ""
    cnt = 0
    quotecnt = 0
    for char in str_file:
        if(char == '"'):
            quotecnt += 1
            new += char
            continue
        elif(char == ';'):
            if(quotecnt % 2 == 0):
                new += char
                cnt += 1
            else:
                new += ','
            continue
        elif(char == '\n'):
            if(quotecnt % 2 == 1 or cnt % rowcnt != 0):
                new += '§'
            else:
                new += char
            continue
        elif(char == '\r'):
            continue
        else:
            new += char
    return new


def import_tier(filename):
    print("starte tier import")

    with open(filename, "r") as fo:
        str_file = fo.read()

    ok = True

    new = clean_str_file(str_file, 11)

    lines = new.split('\n')
    
    for line in lines:
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

    if(ok):
        try:
            db.session.commit()
            tier = db.session.execute("SELECT id FROM tier ORDER BY Id DESC LIMIT 1").fetchone()
            db.session.execute("ALTER SEQUENCE tier_id_seq RESTART WITH " + str(tier['id'] + 1))
            print("tier import ende")
            return True
        except Exception as err:
            print(err)
            print("tier import ende")
            return False
    else:
        db.session.rollback()
        print("tier import ende")
        return False


def import_person(filename):
    print("starte person import")

    with open(filename, "r") as fo:
        str_file = fo.read()

    ok = True

    new = clean_str_file(str_file, 6)

    lines = new.split('\n')

    for line in lines:
        line = line.replace('§', '\n')
        arrline = line.split(";")

        if(len(arrline) != 7):
            print(arrline[0], end="", flush=True)
            continue

        try:
            p_id = int(arrline[0])

            if(p_id < 5000): # hack to limit record count
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

    if(ok):
        try:
            db.session.commit()
            person = db.session.execute("SELECT id FROM person ORDER BY Id DESC LIMIT 1").fetchone()
            db.session.execute("ALTER SEQUENCE person_id_seq RESTART WITH " + str(person['id'] + 1))
            print("person import ende")
            return True
        except Exception as err:
            print(err)
            print("person import ende")
            return False
    else:
        db.session.rollback()
        print("person import ende")
        return False


def import_adresse(filename):
    print("starte adresse import")

    with open(filename, "r") as fo:
        str_file = fo.read()

    ok = True

    new = clean_str_file(str_file, 4)

    lines = new.split('\n')

    personen = db.session.query(Person).all()

    for line in lines:
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

    if(ok):
        try:
            db.session.commit()
            print("adresse import ende")
            return True
        except Exception as err:
            print(err)
            print("adresse import ende")
            return False
    else:
        db.session.rollback()
        print("adresse import ende")
        return False


def import_kontakt(filename):
    print("starte kontakt import")

    with open(filename, "r") as fo:
        str_file = fo.read()

    ok = True

    new = clean_str_file(str_file, 4)

    lines = new.split('\n')

    personen = db.session.query(Person).all()

    for line in lines:
        line = line.replace('§', '\n')
        arrline = line.split(";")

        if(len(arrline) != 5):
            print(arrline[0], end="error", flush=True)
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

    if(ok):
        try:
            db.session.commit()
            print("kontakt import ende")
            return True
        except Exception as err:
            print(err)
            print("kontakt import ende")
            return False
    else:
        db.session.rollback()
        print("kontakt import ende")
        return False


def import_tierhaltung(filename):
    print("starte tierhaltung import")

    with open(filename, "r") as fo:
        str_file = fo.read()

    ok = True

    new = clean_str_file(str_file, 2)

    lines = new.split('\n')

    personen = db.session.query(Person).all()
    
    tiere = db.session.query(Tier).all()

    for line in lines:
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
                for tier in tiere:
                    if(tier.id == tier_id):
                        db.session.delete(tier)
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

    if(ok):
        try:
            db.session.commit()
            tierhaltung = db.session.execute("SELECT id FROM tierhaltung ORDER BY Id DESC LIMIT 1").fetchone()
            db.session.execute("ALTER SEQUENCE tierhaltung_id_seq RESTART WITH " + str(tierhaltung['id'] + 1))
            print("tierhaltung import ende")
            return True
        except Exception as err:
            print(err)
            print("tierhaltung import ende")
            return False
    else:
        db.session.rollback()
        print("tierhaltung import ende")
        return False


def import_behandlung(filename):
    print("starte behandlung import")

    with open(filename, "r") as fo:
        str_file = fo.read()

    ok = True

    new = clean_str_file(str_file, 9)

    lines = new.split('\n')

    tierhaltungen = db.session.query(Tierhaltung).all()

    for line in lines:
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
    
    if(ok):
        try:
            db.session.commit()
            behandlung = db.session.execute("SELECT id FROM behandlung ORDER BY Id DESC LIMIT 1").fetchone()
            db.session.execute("ALTER SEQUENCE behandlung_id_seq RESTART WITH " + str(behandlung['id'] + 1))
            print("behandlung import ende")
            return True
        except Exception as err:
            print(err)
            print("behandlung import ende")
            return False
    else:
        db.session.rollback()
        print("behandlung import ende")
        return False


def import_impfung(filename):
    print("starte impfung import")

    with open(filename, "r") as fo:
        str_file = fo.read()

    ok = True

    new = clean_str_file(str_file, 1)

    lines = new.split('\n')

    behandlungen = db.session.query(Behandlung).all()

    for line in lines:
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

    if(ok):
        try:
            db.session.commit()
            #impfung = db.session.execute("SELECT id FROM impfung ORDER BY Id DESC LIMIT 1").fetchone()
            #db.session.execute("ALTER SEQUENCE impfung_id_seq RESTART WITH " + str(impfung['id'] + 1))
            print("impfung import ende")
            return True
        except Exception as err:
            print(err)
            print("impfung import ende")
            return False
    else:
        db.session.rollback()
        print("impfung import ende")
        return False


def import_behandlungsverlauf(filename):
    print("starte behandlungsverlauf import")

    with open(filename, "r") as fo:
        str_file = fo.read()

    ok = True

    new = clean_str_file(str_file, 5)

    lines = new.split('\n')

    tierhaltungen = db.session.query(Tierhaltung).all()

    for line in lines:
        line = line.replace('§', '\n')

        arrline = line.split(";")

        if(len(arrline) != 6):
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

            behandlungsverlauf = Behandlungsverlauf()

            #behandlungsverlauf.id = int(arrline[0])

            behandlungsverlauf.person_id = person_id

            behandlungsverlauf.tier_id = tier_id

            if(len(arrline[3]) > 0 and len(arrline[3]) >= 10):
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
    
    if(ok):
        try:
            db.session.commit()
            #behandlungsverlauf = db.session.execute("SELECT id FROM behandlungsverlauf ORDER BY Id DESC LIMIT 1").fetchone()
            #db.session.execute("ALTER SEQUENCE behandlungsverlauf_id_seq RESTART WITH " + str(behandlungsverlauf['id'] + 1))
            print("behandlungsverlauf import ende")
            return True
        except Exception as err:
            print(err)
            print("behandlungsverlauf import ende")
            return False
    else:
        db.session.rollback()
        print("behandlungsverlauf import ende")
        return False


def import_rechnung(filename):
    print("starte rechnung import")

    with open(filename, "r") as fo:
        str_file = fo.read()

    ok = True

    new = clean_str_file(str_file, 13)

    lines = new.split('\n')

    tierhaltungen = db.session.query(Tierhaltung).all()

    for line in lines:
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
    
    if(ok):
        try:
            db.session.commit()
            rechnung = db.session.execute("SELECT id FROM rechnung ORDER BY Id DESC LIMIT 1").fetchone()
            db.session.execute("ALTER SEQUENCE rechnung_id_seq RESTART WITH " + str(rechnung['id'] + 1))
            print("rechnung import ende")
            return True
        except Exception as err:
            print(err)
            print("rechnung import ende")
            return False
    else:
        db.session.rollback()
        print("rechnung import ende")
        return False


def import_rechnungszeile(filename):
    print("starte rechnungszeile import")

    with open(filename, "r") as fo:
        str_file = fo.read()

    ok = True

    new = clean_str_file(str_file, 5)

    lines = new.split('\n')

    rechnungen = db.session.query(Rechnung).all()

    for line in lines:
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
    
    if(ok):
        try:
            db.session.commit()
            #rechnungszeile = db.session.execute("SELECT id FROM rechnungszeile ORDER BY Id DESC LIMIT 1").fetchone()
            #db.session.execute("ALTER SEQUENCE rechnungszeile_id_seq RESTART WITH " + str(rechnungszeile['id'] + 1))
            print("rechnungszeile import ende")
            return True
        except Exception as err:
            print(err)
            print("rechnungszeile import ende")
            return False
    else:
        db.session.rollback()
        print("rechnungszeile import ende")
        return False

