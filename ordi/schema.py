

sqldrops = (
    """DROP TABLE IF EXISTS user;""",
    """DROP TABLE IF EXISTS tierhaltung;""",
    """DROP TABLE IF EXISTS person;""",
    """DROP TABLE IF EXISTS kontakt;""",
    """DROP TABLE IF EXISTS adresse;""",
    """DROP TABLE IF EXISTS tier;""",
    """DROP TABLE IF EXISTS behandlung;""",    
    """DROP TABLE IF EXISTS impfung;""",
    """DROP TABLE IF EXISTS behandlungsverlauf;""",
    """DROP TABLE IF EXISTS rechnung;""",
    """DROP TABLE IF EXISTS rechnungszeile;""")

sqlcreates = (
    """CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, \
        username VARCHAR(50) NOT NULL UNIQUE, \
        password VARCHAR(256) NOT NULL);""",
    """CREATE TABLE person (id INTEGER PRIMARY KEY AUTOINCREMENT, \
       anredeartcode INTEGER NOT NULL, \
       titel VARCHAR(40), \
       familienname VARCHAR(40), \
       vorname VARCHAR(40), \
       notiz VARCHAR(200), \
       kunde BOOLEAN NOT NULL DEFAULT true);""",
    """CREATE TABLE adresse (id INTEGER PRIMARY KEY AUTOINCREMENT, \
       person_id INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE, \
       strasse VARCHAR(40), \
       postleitzahl VARCHAR(10), \
       ort VARCHAR(40));""",
    """CREATE TABLE kontakt (id INTEGER PRIMARY KEY AUTOINCREMENT, \
       person_id INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE, \
       kontaktartcode INTEGER NOT NULL, \
       kontakt VARCHAR(50), \
       kontakt_intern VARCHAR(50));""",
    """CREATE TABLE tier (id INTEGER PRIMARY KEY AUTOINCREMENT, \
       tiername VARCHAR(30), \
       tierart VARCHAR(30), \
       rasse VARCHAR(30), \
       farbe VARCHAR(30), \
       viren VARCHAR(30), \
       merkmal VARCHAR(50), \
       geburtsdatum DATE NOT NULL, \
       geschlechtsartcode INTEGER NOT NULL, \
       chip_nummer VARCHAR(30), \
       eu_passnummer VARCHAR(30), \
       patient BOOLEAN NOT NULL DEFAULT true);""",
    """CREATE TABLE behandlung (id INTEGER PRIMARY KEY AUTOINCREMENT, \
       tier_id INTEGER NOT NULL REFERENCES tier(id) ON DELETE CASCADE, \
       behandlungsdatum DATE NOT NULL DEFAULT CURRENT_DATE, \
       gewicht VARCHAR(50), \
       diagnose VARCHAR(1000), \
       laborwerte1 VARCHAR(1000), \
       laborwerte2 VARCHAR(1000), \
       arzneien VARCHAR(255), \
       arzneimittel VARCHAR(100), \
       impfungen_extern VARCHAR(100));""",
    """CREATE TABLE impfung (id INTEGER PRIMARY KEY AUTOINCREMENT, \
        behandlung_id INTEGER NOT NULL REFERENCES behandlung(id) ON DELETE CASCADE, \
        impfungsartcode INTEGER NOT NULL);""",
    """CREATE TABLE tierhaltung (id INTEGER PRIMARY KEY AUTOINCREMENT, \
       person_id INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE, \
       tier_id INTEGER NOT NULL REFERENCES tier(id) ON DELETE CASCADE, \
       anlagezeit TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
       UNIQUE(person_id,tier_id));""",
    """CREATE TABLE behandlungsverlauf (id INTEGER PRIMARY KEY AUTOINCREMENT, \
       person_id INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE, \
       tier_id INTEGER NOT NULL REFERENCES tier(id) ON DELETE CASCADE, \
       datum DATE NOT NULL DEFAULT CURRENT_DATE, \
       diagnose VARCHAR(255), \
       behandlung VARCHAR(1000));""",
    """CREATE TABLE rechnung (id INTEGER PRIMARY KEY AUTOINCREMENT, \
       person_id INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE, \
       tier_id INTEGER NOT NULL REFERENCES tier(id) ON DELETE CASCADE, \
       rechnungsjahr INTEGER NOT NULL, \
       rechnungslfnr INTEGER NOT NULL, \
       ausstellungsdatum DATE NOT NULL DEFAULT CURRENT_DATE, \
       ausstellungsort VARCHAR(255), \
       diagnose VARCHAR(255), \
       bezahlung VARCHAR(255), \
       brutto_summe DECIMAL(10,2) NOT NULL, \
       netto_summe DECIMAL(10,2) NOT NULL, \
       steuerbetrag_zwanzig DECIMAL(10,2) NOT NULL DEFAULT 0, \
       steuerbetrag_dreizehn DECIMAL(10,2) NOT NULL DEFAULT 0, \
       steuerbetrag_zehn DECIMAL(10,2) NOT NULL DEFAULT 0);""",
    """CREATE TABLE rechnungszeile (id INTEGER PRIMARY KEY AUTOINCREMENT, \
       rechnung_id INTEGER NOT NULL REFERENCES rechnung(id) ON DELETE CASCADE, \
       datum DATE NOT NULL DEFAULT CURRENT_DATE, \
       artikelartcode INTEGER NOT NULL, \
       artikel VARCHAR(255), \
       betrag DECIMAL(10,2) NOT NULL);""")

