
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


def delete_db_tierhaltung(id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('SELECT * FROM tierhaltung WHERE tierhaltung.id = ?', (id,))
    tierhaltung = cursor.fetchone()
    cursor.execute('DELETE FROM tierhaltung WHERE id = ?', (id,))
    cursor.execute('DELETE FROM tier WHERE id = ?', (tierhaltung['tier_id'],))    
    cursor.execute('SELECT * FROM tierhaltung WHERE tierhaltung.person_id = ?', (tierhaltung['person_id'],))
    tierhaltungen = cursor.fetchall()
    if(len(tierhaltungen) == 0):
        cursor.execute('DELETE FROM person WHERE id = ?', (tierhaltung['person_id'],))    
    dbcon.commit()
    cursor.close()


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
    cursor.execute('SELECT * FROM behandlung WHERE behandlung.id = ?', (behandlung_id,))
    behandlung = cursor.fetchone()
    cursor.close()
    return behandlung


def read_impfungen(behandlung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute('SELECT * FROM impfung WHERE behandlung_id = ?', (behandlung_id,))
    impfungen = cursor.fetchall()
    cursor.close()
    return impfungen


def read_behandlungsverlauf(behandlungsverlauf_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute('SELECT * FROM behandlungsverlauf WHERE id = ?',(behandlungsverlauf_id,))
    behandlungsverlauf = cursor.fetchone()
    cursor.close()
    return behandlungsverlauf


def read_rechnung(rechnung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute('SELECT * FROM rechnung WHERE rechnung.id = ?',(rechnung_id,))
    rechnung = cursor.fetchone()
    cursor.close()
    return rechnung


def update_rechnung(rechnung_id, rechnungsjahr, rechnungslfnr, ausstellungsdatum, ausstellungsort, diagnose, bezahlung, brutto_summe, netto_summe, steuerbetrag_zwanzig, steuerbetrag_dreizehn, steuerbetrag_zehn):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'UPDATE rechnung SET rechnungsjahr = ?, rechnungslfnr = ?, ausstellungsdatum = ?, ausstellungsort = ?, diagnose = ?, bezahlung = ?, brutto_summe = ?, netto_summe = ?, steuerbetrag_zwanzig = ?, steuerbetrag_dreizehn = ?, steuerbetrag_zehn = ?'
        ' WHERE id = ?',
        (rechnungsjahr, rechnungslfnr, ausstellungsdatum, ausstellungsort, diagnose, bezahlung, brutto_summe, netto_summe, steuerbetrag_zwanzig, steuerbetrag_dreizehn, steuerbetrag_zehn, rechnung_id,)
    )
    dbcon.commit()
    cursor.close()


def delete_db_rechnung(rechnung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('DELETE FROM rechnung WHERE id = ?', (rechnung_id,))
    dbcon.commit()
    cursor.close()


def read_rechnungszeilen(rechnung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute('SELECT * FROM rechnungszeile WHERE rechnung_id = ?',(rechnung_id,))
    rechnungszeilen = cursor.fetchall()
    cursor.close()
    return rechnungszeilen


def read_rechnungszeile(rechnungszeile_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute('SELECT * FROM rechnungszeile WHERE id = ?',(rechnungszeile_id,))
    rechnungszeile = cursor.fetchone()
    cursor.close()
    return rechnungszeile


def write_person(anredeartcode, titel, familienname, vorname, notiz, kunde):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    person_id = cursor.execute(
        'INSERT INTO person (anredeartcode, titel, familienname, vorname, notiz, kunde)'
        ' VALUES (?, ?, ?, ?, ?, ?)',
        (anredeartcode, titel, familienname, vorname, notiz, kunde,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return person_id


def update_person(person_id, anredeartcode, titel, familienname, vorname, notiz, kunde):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'UPDATE person SET anredeartcode = ?, titel = ?, familienname = ?, vorname = ?, notiz = ?, kunde = ?'
        ' WHERE person.id = ?',
        (anredeartcode, titel, familienname, vorname, notiz, kunde, person_id,)
    )
    dbcon.commit()
    cursor.close()


def write_adresse(person_id, strasse, postleitzahl, ort):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    adresse_id = cursor.execute(
        'INSERT INTO adresse (person_id, strasse, postleitzahl, ort)'
        ' VALUES (?, ?, ?, ?)',
        (person_id, strasse, postleitzahl, ort,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return adresse_id


def update_adresse(adresse_id, strasse, postleitzahl, ort):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'UPDATE adresse SET strasse = ?, postleitzahl = ?, ort = ?'
        ' WHERE id = ?',
        (strasse, postleitzahl, ort, adresse_id,)
    )
    dbcon.commit()
    cursor.close()


def delete_db_adresse(adresse_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('DELETE FROM adresse WHERE id = ?', (adresse_id,))
    dbcon.commit()
    cursor.close()


def write_kontakt(person_id, kontaktartcode, kontakt, kontakt_intern):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    kontakt_id = cursor.execute(
        'INSERT INTO kontakt (person_id, kontaktartcode, kontakt, kontakt_intern)'
        ' VALUES (?, ?, ?, ?)',
        (person_id, kontaktartcode, kontakt, kontakt_intern,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return kontakt_id


def update_kontakt(kontakt_id, kontaktartcode, kontakt, kontakt_intern):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'UPDATE kontakt SET kontaktartcode = ?, kontakt = ?, kontakt_intern = ?'
        ' WHERE id = ?',
        (kontaktartcode, kontakt, kontakt_intern, kontakt_id,)
    )
    dbcon.commit()
    cursor.close()


def delete_db_kontakt(kontakt_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('DELETE FROM kontakt WHERE id = ?', (kontakt_id,))
    dbcon.commit()
    cursor.close()


def write_tier(tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    tier_id = cursor.execute(
        'INSERT INTO tier (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return tier_id


def update_tier(tier_id, tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum, geschlechtsartcode, chip_nummer, eu_passnummer, patient):
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


def write_tierhaltung(person_id, tier_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    id = cursor.execute(
        'INSERT INTO tierhaltung (person_id, tier_id)'
        ' VALUES (?, ?)',
        (person_id, tier_id,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return id


def write_behandlung(tier_id, behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    behandlung_id = cursor.execute(
        'INSERT INTO behandlung (tier_id, behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (tier_id, behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return behandlung_id


def update_behandlung(behandlung_id, behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'UPDATE behandlung SET behandlungsdatum = ?, gewicht = ?, diagnose = ?, laborwerte1 = ?, laborwerte2 = ?, arzneien = ?, arzneimittel = ?, impfungen_extern = ?'
        ' WHERE behandlung.id = ?',
        (behandlungsdatum, gewicht, diagnose, laborwerte1, laborwerte2, arzneien, arzneimittel, impfungen_extern, behandlung_id)
    )
    dbcon.commit()
    cursor.close()


def delete_db_behandlung(behandlung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('DELETE FROM behandlung WHERE id = ?', (behandlung_id,))
    dbcon.commit()
    cursor.close()


def write_behandlungsverlauf(person_id, tier_id, datum, diagnose, behandlung):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    behandlungsverlauf_id = cursor.execute(
        'INSERT INTO behandlungsverlauf (person_id, tier_id, datum, diagnose, behandlung)'
        ' VALUES (?, ?, ?, ?, ?)',
        (person_id, tier_id, datum, diagnose, behandlung,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return behandlungsverlauf_id


def update_behandlungsverlauf(behandlungsverlauf_id, datum, diagnose, behandlung):
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


def delete_db_behandlungsverlauf(behandlungsverlauf_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('DELETE FROM behandlungsverlauf WHERE id = ?', (behandlungsverlauf_id,))
    dbcon.commit()
    cursor.close()


def write_rechnung(person_id, tier_id, rechnungsjahr, rechnungslfnr, ausstellungsdatum, ausstellungsort, diagnose, bezahlung, brutto_summe, netto_summe, steuerbetrag_zwanzig, steuerbetrag_dreizehn, steuerbetrag_zehn):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    rechnung_id = cursor.execute(
        'INSERT INTO rechnung (person_id, tier_id, rechnungsjahr, rechnungslfnr, ausstellungsdatum, ausstellungsort, diagnose, bezahlung,'
        ' brutto_summe, netto_summe, steuerbetrag_zwanzig, steuerbetrag_dreizehn, steuerbetrag_zehn)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (person_id, tier_id, rechnungsjahr, rechnungslfnr, ausstellungsdatum, ausstellungsort, diagnose, bezahlung, brutto_summe, netto_summe, steuerbetrag_zwanzig, steuerbetrag_dreizehn, steuerbetrag_zehn,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return rechnung_id


def write_rechnungszeile(rechnung_id, datum, artikelartcode, artikel, betrag):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    rechnungszeile_id = cursor.execute(
        'INSERT INTO rechnungszeile (rechnung_id, datum, artikelartcode, artikel, betrag)'
        ' VALUES (?, ?, ?, ?, ?)',
        (rechnung_id, datum, artikelartcode, artikel, betrag,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return rechnungszeile_id


def update_rechnungszeile(rechnungszeile_id, datum, artikelartcode, artikel, betrag):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'UPDATE rechnungszeile SET datum = ?, artikelartcode = ?, artikel = ?, betrag = ?'
        ' WHERE rechnungszeile.id = ?',
        (datum, artikelartcode, artikel, betrag, rechnungszeile_id,)
    )
    dbcon.commit()
    cursor.close()


def delete_db_rechnungszeile(rechnungszeile_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('DELETE FROM rechnungszeile WHERE id = ?', (rechnungszeile_id,))
    dbcon.commit()
    cursor.close()

