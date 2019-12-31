
#from flask import g

from ordi.db import get_db


def get_karteikarten(familienname, tiername, kunde, patient):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM tierhaltung, person, tier WHERE tierhaltung.person_id = person.id AND tierhaltung.tier_id = tier.id'
        ' AND familienname LIKE ? AND tiername LIKE ? AND kunde = ? AND patient = ?'
        ' ORDER BY familienname ASC',
        (familienname + "%", tiername + "%", kunde, patient,)
    )
    karteikarten = cursor.fetchall()
    cursor.close()
    return karteikarten


def get_verlaeufe(behandlungsjahr):
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
    verlaeufe = cursor.fetchall()
    cursor.close()
    return verlaeufe


def get_karteikarte(id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM tierhaltung, person, tier'
        ' WHERE tierhaltung.id = ? AND tierhaltung.person_id = person.id AND tierhaltung.tier_id = tier.id',
        (id,)
    )
    karteikarte = cursor.fetchone()
    cursor.close()
    return karteikarte


def get_karteikarte_by_children(person_id, tier_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT * FROM tierhaltung, person, tier'
        ' WHERE tierhaltung.person_id = ? AND tierhaltung.tier_id = ?',
        (person_id, tier_id,)
    )
    karteikarte = cursor.fetchone()
    cursor.close()
    return karteikarte


def get_person(person_id):
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


def get_tier(tier_id):
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


def get_adresse(person_id):
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


def get_kontakte(person_id):
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


def get_behandlungen(id):
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


def get_behandlungsverlauf(behandlungsverlauf_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute(
        'SELECT * FROM behandlungsverlauf WHERE id = ?',
        (behandlungsverlauf_id,)
    )
    behandlungsverlauf = cursor.fetchone()
    cursor.close()
    return behandlungsverlauf

