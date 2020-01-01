
#from flask import g

from ordi.db import get_db


def read_tierhaltungen(familienname, tiername, kunde, patient):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM tierhaltung, person, tier WHERE tierhaltung.person_id = person.id AND tierhaltung.tier_id = tier.id'
        ' AND familienname LIKE ? AND tiername LIKE ? AND kunde = ? AND patient = ?'
        ' ORDER BY familienname ASC',
        (familienname + "%", tiername + "%", kunde, patient,)
    )
    tierhaltungen = cursor.fetchall()
    cursor.close()
    return tierhaltungen


def read_behandlungsverlaeufe(behandlungsjahr):
    begin = str(behandlungsjahr) + "-01-01"
    end = str(behandlungsjahr + 1) + "-01-01"
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM behandlungsverlauf, person, tier'
        ' WHERE behandlungsverlauf.person_id = person.id AND behandlungsverlauf.tier_id = tier.id'
        ' AND behandlungsverlauf.datum >  ? AND behandlungsverlauf.datum <  ?'
        ' ORDER BY behandlungsverlauf.datum ASC',
        (begin, end,)
    )
    behandlungsverlaeufe = cursor.fetchall()
    cursor.close()
    return behandlungsverlaeufe


def read_tierhaltung(id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM tierhaltung, person, tier'
        ' WHERE tierhaltung.id = ? AND tierhaltung.person_id = person.id AND tierhaltung.tier_id = tier.id',
        (id,)
    )
    tierhaltung = cursor.fetchone()
    cursor.close()
    return tierhaltung


def read_tierhaltung_by_children(person_id, tier_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM tierhaltung, person, tier'
        ' WHERE tierhaltung.person_id = ? AND tierhaltung.tier_id = ?',
        (person_id, tier_id,)
    )
    tierhaltung = cursor.fetchone()
    cursor.close()
    return tierhaltung


def read_person(person_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM person WHERE person.id = ?',
        (person_id,)
    )
    person = cursor.fetchone()
    cursor.close()
    return person


def read_tier(tier_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM tier WHERE tier.id = ?',
        (tier_id,)
    )
    tier = cursor.fetchone()
    cursor.close()
    return tier


def read_adresse(person_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM adresse WHERE adresse.person_id = ?',
        (person_id,)
    )
    adresse = cursor.fetchone()
    cursor.close()
    return adresse


def read_kontakte(person_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM kontakt WHERE kontakt.person_id = ?',
        (person_id,)
    )
    kontakte = cursor.fetchall()
    cursor.close()
    return kontakte


def read_behandlungen(id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute(
        'SELECT * FROM behandlung JOIN tierhaltung ON behandlung.tier_id = tierhaltung.tier_id'
        ' WHERE tierhaltung.id = ? ORDER BY behandlungsdatum ASC',
        (id,)
    )
    behandlungen = cursor.fetchall()
    cursor.close()
    return behandlungen


def read_behandlungsverlauf(behandlungsverlauf_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute(
        'SELECT * FROM behandlungsverlauf WHERE id = ?',
        (behandlungsverlauf_id,)
    )
    behandlungsverlauf = cursor.fetchone()
    cursor.close()
    return behandlungsverlauf

