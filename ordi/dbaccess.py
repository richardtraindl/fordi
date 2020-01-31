
#from flask import g

from ordi.db2 import get_db
from ordi.values import IMPFUNG
from ordi.models import *


# tierhaltung
def read_tierhaltungen(familienname, tiername, kunde, patient):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        'SELECT tierhaltung.id, tierhaltung.person_id, tierhaltung.tier_id, anlagezeit,'
        ' anredecode, titel, familienname, vorname, notiz, kunde,'
        ' tiername, tierart, rasse, farbe, viren, merkmal, geburtsdatum as "geburtsdatum [date]", '
        ' geschlechtscode, chip_nummer, eu_passnummer, patient'
        ' FROM tierhaltung, person, tier WHERE tierhaltung.person_id = person.id AND tierhaltung.tier_id = tier.id'
        ' AND familienname LIKE ? AND tiername LIKE ? AND kunde = ? AND patient = ?'
        ' ORDER BY familienname ASC',
        (familienname + "%", tiername + "%", kunde, patient,)
    )
    tierhaltungen = cursor.fetchall()
    cursor.close()
    return tierhaltungen


def fill_tierhaltung_person_and_tier(tierhaltung):
    ctierhaltung = cTierhaltung(int(tierhaltung['id']), 
                                int(tierhaltung['person_id']), 
                                int(tierhaltung['tier_id']))

    cperson = cPerson(int(tierhaltung['person_id']), 
                      int(tierhaltung['anredecode']), 
                      tierhaltung['titel'], 
                      tierhaltung['familienname'], 
                      tierhaltung['vorname'], 
                      tierhaltung['notiz'], 
                      int(tierhaltung['kunde']))

    ctier = cTier(int(tierhaltung['tier_id']), 
                  tierhaltung['tiername'], 
                  tierhaltung['tierart'], 
                  tierhaltung['rasse'], 
                  tierhaltung['farbe'], 
                  tierhaltung['viren'], 
                  tierhaltung['merkmal'], 
                  tierhaltung['geburtsdatum'], 
                  int(tierhaltung['geschlechtscode']),
                  tierhaltung['chip_nummer'], 
                  tierhaltung['eu_passnummer'], 
                  int(tierhaltung['patient']))

    return ctierhaltung, cperson, ctier

def read_tierhaltung(id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "SELECT * FROM tierhaltung, person, tier"
        " WHERE tierhaltung.id = ? AND tierhaltung.person_id = person.id"
        " AND tierhaltung.tier_id = tier.id",
        (id,)
    )
    tierhaltung = cursor.fetchone()
    cursor.close()

    ctierhaltung, cperson, ctier = fill_tierhaltung_person_and_tier(tierhaltung)
    return ctierhaltung, cperson, ctier


def read_tierhaltung_by_children(person_id, tier_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "SELECT * FROM tierhaltung, person, tier"
        " WHERE tierhaltung.person_id = person.id"
        " AND tierhaltung.tier_id = tier.id"
        " AND tierhaltung.person_id = ? AND tierhaltung.tier_id = ?",
        (person_id, tier_id,)
    )
    tierhaltung = cursor.fetchone()
    cursor.close()

    ctierhaltung, cperson, ctier = fill_tierhaltung_person_and_tier(tierhaltung)
    return ctierhaltung, cperson, ctier


def write_tierhaltung(ctierhaltung):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    ctierhaltung.id = cursor.execute(
        "INSERT INTO tierhaltung (person_id, tier_id)"
        " VALUES (?, ?)",
        (ctierhaltung.person_id, ctierhaltung.tier_id,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return True


def delete_db_tierhaltung(id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("SELECT * FROM tierhaltung WHERE tierhaltung.id = ?", (id,))
    tierhaltung = cursor.fetchone()
    cursor.execute("DELETE FROM tierhaltung WHERE id = ?", (id,))
    cursor.execute("DELETE FROM tier WHERE id = ?", (tierhaltung['tier_id'],))    
    cursor.execute("SELECT * FROM tierhaltung WHERE tierhaltung.person_id = ?", (tierhaltung['person_id'],))
    tierhaltungen = cursor.fetchall()
    if(len(tierhaltungen) == 0):
        cursor.execute("DELETE FROM person WHERE id = ?", (tierhaltung['person_id'],))    
    dbcon.commit()
    cursor.close()
    return True
# tierhaltung


# person
def read_person(person_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "SELECT * FROM person WHERE person.id = ?",
        (person_id,)
    )
    person = cursor.fetchone()
    cursor.close()
    cperson = cPerson(int(person['id']), int(person['anredecode']), person['titel'], person['familienname'], person['vorname'], person['notiz'], int(person['kunde']))
    return cperson


def write_person(cperson):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cperson.id = cursor.execute(
        "INSERT INTO person (anredecode, titel, familienname, vorname, notiz, kunde)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (cperson.anredecode, cperson.titel, cperson.familienname, cperson.vorname, cperson.notiz, cperson.kunde,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return True


def update_person(cperson):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "UPDATE person SET anredecode = ?, titel = ?, familienname = ?, vorname = ?, notiz = ?, kunde = ?"
        " WHERE id = ?",
        (cperson.anredecode, cperson.titel, cperson.familienname, cperson.vorname, cperson.notiz, cperson.kunde, cperson.id,)
    )
    dbcon.commit()
    cursor.close()
    return True
# person


# adresse
def read_adresse_for_person(person_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "SELECT * FROM adresse WHERE adresse.person_id = ?",
        (person_id,)
    )
    adresse = cursor.fetchone()
    cursor.close()
    if(adresse):
        cadresse = cAdresse(int(adresse['id']), int(adresse['person_id']), adresse['strasse'], adresse['postleitzahl'], adresse['ort'])
    else:
        cadresse = None
    return cadresse


def write_adresse(cadresse):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cadresse.id = cursor.execute(
        "INSERT INTO adresse (person_id, strasse, postleitzahl, ort)"
        " VALUES (?, ?, ?, ?)",
        (cadresse.person_id, cadresse.strasse, cadresse.postleitzahl, cadresse.ort,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return True


def update_adresse(cadresse):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "UPDATE adresse SET strasse = ?, postleitzahl = ?, ort = ?"
        " WHERE id = ?",
        (cadresse.strasse, cadresse.postleitzahl, cadresse.ort, cadresse.id,)
    )
    dbcon.commit()
    cursor.close()
    return True


def delete_db_adresse(adresse_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("DELETE FROM adresse WHERE id = ?", (adresse_id,))
    dbcon.commit()
    cursor.close()
    return True
# adresse


# kontakt
def read_kontakte_for_person(person_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "SELECT * FROM kontakt WHERE kontakt.person_id = ?",
        (person_id,)
    )
    kontakte = cursor.fetchall()
    cursor.close()
    ckontakte = []
    for kontakt in kontakte:
        ckontakte.append(cKontakt(int(kontakt['id']), int(kontakt['person_id']), int(kontakt['kontaktcode']), kontakt['kontakt'], kontakt['kontakt_intern']))
    return ckontakte


def write_kontakt(ckontakt):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    ckontakt.id = cursor.execute(
        "INSERT INTO kontakt (person_id, kontaktcode, kontakt, kontakt_intern)"
        " VALUES (?, ?, ?, ?)",
        (ckontakt.person_id, ckontakt.kontaktcode, ckontakt.kontakt, ckontakt.kontakt_intern,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return True


def update_kontakt(ckontakt):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "UPDATE kontakt SET kontaktcode = ?, kontakt = ?, kontakt_intern = ?"
        " WHERE id = ?",
        (ckontakt.kontaktcode, ckontakt.kontakt, ckontakt.kontakt_intern, ckontakt.id,)
    )
    dbcon.commit()
    cursor.close()
    return True


def delete_db_kontakt(kontakt_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("DELETE FROM kontakt WHERE id = ?", (kontakt_id,))
    dbcon.commit()
    cursor.close()
    return True
# kontakt


# tier
def read_tier(tier_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "SELECT * FROM tier WHERE tier.id = ?",
        (tier_id,)
    )
    tier = cursor.fetchone()
    cursor.close()
    ctier = cTier(int(tier['id']), tier['tiername'], tier['tierart'], tier['rasse'], tier['farbe'], 
                  tier['viren'], tier['merkmal'], tier['geburtsdatum'], int(tier['geschlechtscode']),
                  tier['chip_nummer'], tier['eu_passnummer'], int(tier['patient']))
    return ctier


def write_tier(ctier):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    ctier.id = cursor.execute(
        "INSERT INTO tier (tiername, tierart, rasse, farbe, viren," 
        " merkmal, geburtsdatum, geschlechtscode, chip_nummer,"
        " eu_passnummer, patient)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (ctier.tiername, ctier.tierart, ctier.rasse, ctier.farbe, ctier.viren, 
         ctier.merkmal, ctier.geburtsdatum, ctier.geschlechtscode, ctier.chip_nummer, 
         ctier.eu_passnummer, ctier.patient,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return True


def update_tier(ctier):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "UPDATE tier SET tiername = ?, tierart = ?, rasse = ?, farbe = ?, viren = ?,"
        " merkmal = ?, geburtsdatum = ?, geschlechtscode = ?, chip_nummer = ?,"
        " eu_passnummer = ?, patient = ?"
        " WHERE id = ?",
        (ctier.tiername, ctier.tierart, ctier.rasse, ctier.farbe, ctier.viren, 
         ctier.merkmal, ctier.geburtsdatum, ctier.geschlechtscode, ctier.chip_nummer, 
         ctier.eu_passnummer, ctier.patient, ctier.id,)
    )
    dbcon.commit()
    cursor.close()
    return True
# tier


# behandlung
def read_behandlungen_for_tier(tier_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute(
        "SELECT * FROM behandlung JOIN tier ON behandlung.tier_id = tier.id"
        " WHERE tier.id = ? ORDER BY behandlungsdatum ASC, id ASC",
        (tier_id,)
    )
    behandlungen = cursor.fetchall()
    cbehandlungen = []
    for behandlung in behandlungen:
        cbehandlung = cBehandlung(int(behandlung['id']), int(behandlung['tier_id']), behandlung['behandlungsdatum'], behandlung['gewicht'],  
                                  behandlung['diagnose'], behandlung['laborwerte1'], behandlung['laborwerte2'], behandlung['arzneien'],
                                  behandlung['arzneimittel'], behandlung['impfungen_extern'])

        cursor.execute("SELECT * FROM impfung WHERE behandlung_id = ?", (cbehandlung.id,))
        impfungen = cursor.fetchall()
        for impfung in impfungen:
            cimpfung = cImpfung(int(impfung['id']), int(impfung['behandlung_id']), int(impfung['impfungscode'])) 
            cbehandlung.impfungen.append(cimpfung)
        cbehandlungen.append(cbehandlung)
    cursor.close()
    return cbehandlungen


def read_behandlung(behandlung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("SELECT * FROM behandlung WHERE behandlung.id = ?", (behandlung_id,))
    behandlung = cursor.fetchone()
    cursor.close()
    cbehandlung = cBehandlung(int(behandlung['id']), int(behandlung['tier_id']), behandlung['behandlungsdatum'], behandlung['gewicht'],  
                                  behandlung['diagnose'], behandlung['laborwerte1'], behandlung['laborwerte2'], behandlung['arzneien'],
                                  behandlung['arzneimittel'], behandlung['impfungen_extern'])
    return cbehandlung


def write_behandlung(cbehandlung):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cbehandlung.id = cursor.execute(
        "INSERT INTO behandlung (tier_id, behandlungsdatum, gewicht,"
        " diagnose, laborwerte1, laborwerte2,"
        " arzneien, arzneimittel, impfungen_extern)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (cbehandlung.tier_id, cbehandlung.behandlungsdatum, cbehandlung.gewicht, 
         cbehandlung.diagnose, cbehandlung.laborwerte1, cbehandlung.laborwerte2, 
         cbehandlung.arzneien, cbehandlung.arzneimittel, cbehandlung.impfungen_extern,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return True


def update_behandlung(cbehandlung):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "UPDATE behandlung SET behandlungsdatum = ?, gewicht = ?, diagnose = ?,"
        " laborwerte1 = ?, laborwerte2 = ?, arzneien = ?,"
        " arzneimittel = ?, impfungen_extern = ?"
        " WHERE id = ?",
        (cbehandlung.behandlungsdatum, cbehandlung.gewicht, cbehandlung.diagnose, 
         cbehandlung.laborwerte1, cbehandlung.laborwerte2, cbehandlung.arzneien, 
         cbehandlung.arzneimittel, cbehandlung.impfungen_extern, cbehandlung.id)
    )
    dbcon.commit()
    cursor.close()
    return True


def delete_db_behandlung(behandlung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("DELETE FROM behandlung WHERE id = ?", (behandlung_id,))
    dbcon.commit()
    cursor.close()
    return True
# behandlung


# impfung
def save_or_delete_impfungen(behandlung_id, impfungstexte):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("SELECT * FROM impfung WHERE behandlung_id = ?", (behandlung_id,))
    sql_impfungen = cursor.fetchall()

    for impfungstext in impfungstexte:
        try:
            impfungscode = IMPFUNG[impfungstext]
        except:
            print("severe error")
            cursor.close()
            return False
        found = False
        for sql_impfung in sql_impfungen:
            if(impfungscode == sql_impfung['impfungscode']):
                found = True
                break
        if(found == False):
            cursor.execute("INSERT INTO impfung (behandlung_id, impfungscode) VALUES (?, ?)",
                           (behandlung_id, impfungscode,))
            dbcon.commit()

    for sql_impfung in sql_impfungen:
        found = False
        for impfungstext in impfungstexte:
            impfungscode = IMPFUNG[impfungstext]
            if(impfungscode == sql_impfung['impfungscode']):
                found = True
                break
        if(found == False):
            cursor.execute("DELETE FROM impfung WHERE id = ?", (sql_impfung['id'],))
            dbcon.commit()
    cursor.close()
    return True
# impfung


# behandlungsverlauf
def read_behandlungsverlaeufe(behandlungsjahr):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    if(behandlungsjahr):
        begin = str(behandlungsjahr - 1) + "-12-31"
        end = str(behandlungsjahr + 1) + "-01-01"
        cursor.execute(
            "SELECT * FROM behandlungsverlauf, person, tier"
            " WHERE behandlungsverlauf.person_id = person.id"
            " AND behandlungsverlauf.tier_id = tier.id"
            " AND behandlungsverlauf.datum > ? AND behandlungsverlauf.datum <  ?"
            " ORDER BY behandlungsverlauf.datum ASC",
            (begin, end,)
        )
    else:
        cursor.execute(
            "SELECT * FROM behandlungsverlauf, person, tier"
            " WHERE behandlungsverlauf.person_id = person.id"
            " AND behandlungsverlauf.tier_id = tier.id"
            " ORDER BY behandlungsverlauf.datum ASC"
        )
    behandlungsverlaeufe = cursor.fetchall()
    cursor.close()
    return behandlungsverlaeufe


def read_behandlungsverlauf(behandlungsverlauf_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("SELECT * FROM behandlungsverlauf WHERE id = ?",(behandlungsverlauf_id,))
    behandlungsverlauf = cursor.fetchone()
    cursor.close()
    cbehandlungsverlauf = cBehandlungsverlauf(int(behandlungsverlauf['id']), 
                                              int(behandlungsverlauf['person_id']), 
                                              int(behandlungsverlauf['tier_id']), 
                                              behandlungsverlauf['datum'], 
                                              behandlungsverlauf['diagnose'],  
                                              behandlungsverlauf['behandlung'])
    return cbehandlungsverlauf


def write_behandlungsverlauf(cbehandlungsverlauf):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cbehandlungsverlauf.id = cursor.execute(
        "INSERT INTO behandlungsverlauf (person_id, tier_id, datum, diagnose, behandlung)"
        " VALUES (?, ?, ?, ?, ?)",
        (cbehandlungsverlauf.person_id, cbehandlungsverlauf.tier_id, cbehandlungsverlauf.datum, 
         cbehandlungsverlauf.diagnose, cbehandlungsverlauf.behandlung,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return True


def update_behandlungsverlauf(cbehandlungsverlauf):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "UPDATE behandlungsverlauf SET datum = ?, diagnose = ?, behandlung = ?"
        " WHERE id = ?",
        (cbehandlungsverlauf.datum, cbehandlungsverlauf.diagnose, 
         cbehandlungsverlauf.behandlung, cbehandlungsverlauf.id,)
    )
    dbcon.commit()
    cursor.close()
    return True


def delete_db_behandlungsverlauf(behandlungsverlauf_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("DELETE FROM behandlungsverlauf WHERE id = ?", (behandlungsverlauf_id,))
    dbcon.commit()
    cursor.close()
    return True
# behandlungsverlauf


# rechnung
def read_rechnungen(rechnungsjahr):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    if(rechnungsjahr):
        cursor.execute(
            "SELECT * FROM rechnung, person, tier"
            " WHERE rechnung.person_id = person.id"
            " AND rechnung.tier_id = tier.id"
            " AND rechnung.rechnungsjahr = ?"
            " ORDER BY rechnungsjahr, rechnungslfnr ASC",
            (rechnungsjahr,)
        )
    else:
        cursor.execute(
            "SELECT * FROM rechnung, person, tier"
            " WHERE rechnung.person_id = person.id"
            " AND rechnung.tier_id = tier.id"
            " ORDER BY rechnungsjahr, rechnungslfnr ASC"
        )
    rechnungen = cursor.fetchall()
    cursor.close()
    return rechnungen


def read_rechnung(rechnung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("SELECT * FROM rechnung WHERE id = ?",(rechnung_id,))
    rechnung = cursor.fetchone()
    cursor.close()

    if(rechnung):
        crechnung = cRechnung(int(rechnung['id']), 
                              int(rechnung['person_id']),
                              int(rechnung['tier_id']), 
                              int(rechnung['rechnungsjahr']), 
                              int(rechnung['rechnungslfnr']),  
                              rechnung['ausstellungsdatum'],
                              rechnung['ausstellungsort'], 
                              rechnung['diagnose'], 
                              rechnung['bezahlung'],
                              float(rechnung['brutto_summe']),
                              float(rechnung['netto_summe']),
                              float(rechnung['steuerbetrag_zwanzig']),
                              float(rechnung['steuerbetrag_dreizehn']),
                              float(rechnung['steuerbetrag_zehn']))
    else:
        crechnung = None
    return crechnung


def write_rechnung(crechung):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    crechung.id = cursor.execute(
        "INSERT INTO rechnung (person_id, tier_id, rechnungsjahr, rechnungslfnr,"
        " ausstellungsdatum, ausstellungsort, diagnose,"
        " bezahlung, brutto_summe, netto_summe, steuerbetrag_zwanzig,"
        " steuerbetrag_dreizehn, steuerbetrag_zehn)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (crechung.person_id, crechung.tier_id, crechung.rechnungsjahr, crechung.rechnungslfnr, 
         crechung.ausstellungsdatum, crechung.ausstellungsort, crechung.diagnose, 
         crechung.bezahlung, crechung.brutto_summe, crechung.netto_summe, crechung.steuerbetrag_zwanzig, 
         crechung.steuerbetrag_dreizehn, crechung.steuerbetrag_zehn,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return True


def update_rechnung(crechnung):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "UPDATE rechnung SET rechnungsjahr = ?, rechnungslfnr = ?, ausstellungsdatum = ?,"
        " ausstellungsort = ?, diagnose = ?, bezahlung = ?,"
        " brutto_summe = ?, netto_summe = ?, steuerbetrag_zwanzig = ?,"
        " steuerbetrag_dreizehn = ?, steuerbetrag_zehn = ?"
        " WHERE id = ?",
        (crechnung.rechnungsjahr, crechnung.rechnungslfnr, crechnung.ausstellungsdatum, 
         crechnung.ausstellungsort, crechnung.diagnose, crechnung.bezahlung, 
         crechnung.brutto_summe, crechnung.netto_summe, crechnung.steuerbetrag_zwanzig, 
         crechnung.steuerbetrag_dreizehn, crechnung.steuerbetrag_zehn, crechnung.id,)
    )
    dbcon.commit()
    cursor.close()
    return True


def delete_db_rechnung(rechnung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("DELETE FROM rechnung WHERE id = ?", (rechnung_id,))
    dbcon.commit()
    cursor.close()
    return True
# rechnung


# rechnungszeile
def read_rechnungszeilen_for_rechnung(rechnung_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("SELECT * FROM rechnungszeile WHERE rechnung_id = ?",(rechnung_id,))
    rechnungszeilen = cursor.fetchall()
    cursor.close()

    crechnungszeilen = []
    for rechnungszeile in rechnungszeilen:
        crechnungszeile = cRechnungszeile(int(rechnungszeile['id']), 
                                          int(rechnungszeile['rechnung_id']), 
                                          rechnungszeile['datum'], 
                                          int(rechnungszeile['artikelcode']), 
                                          rechnungszeile['artikel'],
                                          float(rechnungszeile['betrag']))
        crechnungszeilen.append(crechnungszeile)
    return crechnungszeilen


def read_rechnungszeile(rechnungszeile_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("SELECT * FROM rechnungszeile WHERE id = ?",(rechnungszeile_id,))
    rechnungszeile = cursor.fetchone()
    cursor.close()
    if(rechnungszeile):
        crechnungszeile = cRechnungszeile(int(rechnungszeile['id']), 
                                          int(rechnungszeile['rechnung_id']), 
                                          rechnungszeile['datum'], 
                                          int(rechnungszeile['artikelcode']), 
                                          rechnungszeile['artikel'],
                                          float(rechnungszeile['betrag']))
    else:
        crechnungszeile = None
    return crechnungszeile


def write_rechnungszeile(crechnungszeile):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    crechnungszeile.id = cursor.execute(
        "INSERT INTO rechnungszeile (rechnung_id, datum, artikelcode,"
        " artikel, betrag)"
        " VALUES (?, ?, ?, ?, ?)",
        (crechnungszeile.rechnung_id, crechnungszeile.datum, crechnungszeile.artikelcode, 
         crechnungszeile.artikel, crechnungszeile.betrag,)
    ).lastrowid
    dbcon.commit()
    cursor.close()
    return True


def update_rechnungszeile(crechnungszeile):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute(
        "UPDATE rechnungszeile SET datum = ?, artikelcode = ?,"
        " artikel = ?, betrag = ?"
        " WHERE id = ?",
        (crechnungszeile.datum, crechnungszeile.artikelcode, crechnungszeile.artikel, 
         crechnungszeile.betrag, crechnungszeile.id,)
    )
    dbcon.commit()
    cursor.close()
    return True


def delete_db_rechnungszeile(rechnungszeile_id):
    dbcon = get_db()
    cursor = dbcon.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("DELETE FROM rechnungszeile WHERE id = ?", (rechnungszeile_id,))
    dbcon.commit()
    cursor.close()
# rechnungszeile

