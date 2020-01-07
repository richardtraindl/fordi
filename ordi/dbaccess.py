
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
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    if(behandlungsjahr):
        begin = str(behandlungsjahr - 1) + "-12-31"
        end = str(behandlungsjahr + 1) + "-01-01"
        cursor.execute(
            'SELECT * FROM behandlungsverlauf, person, tier'
            ' WHERE behandlungsverlauf.person_id = person.id'
            ' AND behandlungsverlauf.tier_id = tier.id'
            ' AND behandlungsverlauf.datum > ? AND behandlungsverlauf.datum <  ?'
            ' ORDER BY behandlungsverlauf.datum ASC',
            (begin, end,)
        )
    else:
        cursor.execute(
            'SELECT * FROM behandlungsverlauf, person, tier'
            ' WHERE behandlungsverlauf.person_id = person.id'
            ' AND behandlungsverlauf.tier_id = tier.id'
            ' ORDER BY behandlungsverlauf.datum ASC'
        )
    behandlungsverlaeufe = cursor.fetchall()
    cursor.close()
    return behandlungsverlaeufe


def read_rechnungen(rechnungsjahr):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    if(rechnungsjahr):
        cursor.execute(
            'SELECT * FROM rechnung, person, tier'
            ' WHERE rechnung.person_id = person.id'
            ' AND rechnung.tier_id = tier.id'
            ' AND rechnung.rechnungsjahr = ?'
            ' ORDER BY rechnungsjahr, rechnungslfnr ASC',
            (rechnungsjahr,)
        )
    else:
        cursor.execute(
            'SELECT * FROM rechnung, person, tier'
            ' WHERE rechnung.person_id = person.id'
            ' AND rechnung.tier_id = tier.id'
            ' ORDER BY rechnungsjahr, rechnungslfnr ASC'
        )
    rechnungen = cursor.fetchall()
    cursor.close()
    return rechnungen


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


def read_behandlung(behandlung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute(
        'SELECT * FROM behandlung WHERE id = ?', (behandlung_id,)
    )
    behandlung = cursor.fetchone()
    cursor.close()
    return behandlung


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


def read_rechnung(rechnung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute(
        'SELECT * FROM rechnung WHERE rechnung.id = ?',
        (rechnung_id,)
    )
    rechnung = cursor.fetchone()
    cursor.close()
    return rechnung


def read_rechnungszeilen(rechnung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute(
        'SELECT * FROM rechnungszeile WHERE rechnung_id = ?',
        (rechnung_id,)
    )
    rechnungszeilen = cursor.fetchall()
    cursor.close()
    return rechnungszeilen


def read_rechnungszeile(rechnungszeile_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute(
        'SELECT * FROM rechnungszeile WHERE id = ?',
        (rechnungszeile_id,)
    )
    rechnungszeile = cursor.fetchone()
    cursor.close()
    return rechnungszeile

