sqldrops = (
    """DROP TABLE IF EXISTS auth_user CASCADE;""",
    """DROP TABLE IF EXISTS tierhaltung CASCADE;""",
    """DROP TABLE IF EXISTS person CASCADE;""",
    """DROP TABLE IF EXISTS kontakt CASCADE;""",
    """DROP TABLE IF EXISTS adresse CASCADE;""",
    """DROP TABLE IF EXISTS tier CASCADE;""",
    """DROP TABLE IF EXISTS behandlung CASCADE;""",    
    """DROP TABLE IF EXISTS impfung CASCADE;""",
    """DROP TABLE IF EXISTS behandlungsverlauf CASCADE;""".
    """DROP TABLE IF EXISTS rechnung CASCADE;""",
    """DROP TABLE IF EXISTS rechnungszeile CASCADE;""")


sqlcreates = (
    """CREATE TABLE auth_user (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
        username VARCHAR(50) NOT NULL UNIQUE, \
        password VARCHAR(256) NOT NULL);""",
    """CREATE TABLE person (id SERIAL PRIMARY KEY, \
       anredeartcode INTEGER NOT NULL, \
       titel VARCHAR(40), \
       familienname VARCHAR(40), \
       vorname VARCHAR(40), \
       notiz VARCHAR(200), \
       kunde BOOLEAN NOT NULL DEFAULT true);""",
    """CREATE TABLE adresse (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
       person_id INTEGER REFERENCES person(id) ON DELETE CASCADE, \
       strasse VARCHAR(40), \
       postleitzahl VARCHAR(10), \
       ort VARCHAR(40));""",
    """CREATE TABLE kontakt (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
       person_id INTEGER REFERENCES person(id) ON DELETE CASCADE, \
       kontaktartcode INTEGER NOT NULL, \
       kontakt VARCHAR(50), \
       kontakt_intern VARCHAR(50));""",
    """CREATE TABLE tier (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
       tiername VARCHAR(30), \
       tierart VARCHAR(30), \
       rasse VARCHAR(30), \
       farbe VARCHAR(30), \
       viren VARCHAR(30), \
       merkmal VARCHAR(50), \
       geburtsdatum DATE NOT NULL, \
       geschlechtsartCode INTEGER NOT NULL, \
       chip_nummer VARCHAR(30), \
       eu_passnummer VARCHAR(30), \
       patient BOOLEAN NOT NULL DEFAULT true);""",
    """CREATE TABLE behandlung (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
       tier_id INTEGER REFERENCES tier(id) ON DELETE CASCADE, \
       behandlungsdatum TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
       gewicht_Kg VARCHAR(50), \
       diagnose VARCHAR(1000), \
       laborwerte1 VARCHAR(1000), \
       laborwerte2 VARCHAR(1000), \
       arzneien VARCHAR(255), \
       arzneimittel VARCHAR(100), \
       impfungen_extern VARCHAR(100));""",
    """CREATE TABLE impfung (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
        behandlung_id INTEGER REFERENCES beahndlung(id) ON DELETE CASCADE, \
        impfungsartcode INTEGER NOT NULL);""",
    """CREATE TABLE behandlungsverlauf (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
       person_id INTEGER REFERENCES person(id) ON DELETE CASCADE, \
       tier_id INTEGER REFERENCES tier(id) ON DELETE CASCADE, \
       datum TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
       diagnose VARCHAR(255), \
       behandlung VARCHAR(1000));""")
    """CREATE TABLE tierhaltung (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
       person_id INTEGER REFERENCES person(id) ON DELETE CASCADE, \
       tier_id INTEGER REFERENCES tier(id) ON DELETE CASCADE, \
       anlagedatum TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);""")
    """CREATE TABLE rechnung (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
       person_id INTEGER REFERENCES person(id) ON DELETE CASCADE, \
       tier_id INTEGER REFERENCES tier(id) ON DELETE CASCADE, \
       rechnungjahr INTEGER NOT NULL, \
       rechnunglfnr INTEGER NOT NULL, \
       datum DATE NOT NULL DEFAULT NOW, \
       ort VARCHAR(255), \
       diagnose VARCHAR(255), \
       zahlung VARCHAR(255), \
       brutto_summe DECIMAL(10,2) NOT NULL, \
       netto_summe DECIMAL(10,2) NOT NULL, \
       steuerbetrag_zwanzig DECIMAL(10,2) NOT NULL DEFAULT 0, \
       steuerbetrag_dreizehn DECIMAL(10,2) NOT NULL DEFAULT 0, \
       steuerbetrag_zehn DECIMAL(10,2) NOT NULL DEFAULT 0);""")
    """CREATE TABLE rechnungzeile (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, \
       rechnung_id INTEGER REFERENCES rechnung(id) ON DELETE CASCADE, \
       artikelartcode INTEGER NOT NULL, \
       datum DATE NOT NULL DEFAULT NOW, \
       artikel VARCHAR(255), \
       betrag DECIMAL(10,2) NOT NULL);""")

