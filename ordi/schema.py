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
    """CREATE TABLE auth_user (id SERIAL PRIMARY KEY, \
        username VARCHAR(50) NOT NULL, \
        password VARCHAR(256) NOT NULL, UNIQUE(username));""",
    """CREATE TABLE person (id SERIAL PRIMARY KEY, \
       AnredeartCode INTEGER NOT NULL, \
       Titel VARCHAR(40), \
       Familienname VARCHAR(40), \
       Vorname VARCHAR(40), \
       Notiz VARCHAR(200), \
       Kunde BOOLEAN NOT NULL DEFAULT true);""",
    """CREATE TABLE adresse (id SERIAL PRIMARY KEY, \
       person_id INTEGER REFERENCES person(id) ON DELETE CASCADE, \
       Strasse VARCHAR(40), \
       Postleitzahl VARCHAR(10), \
       Ort VARCHAR(40));""",
    """CREATE TABLE kontakt (id SERIAL PRIMARY KEY, \
       person_id INTEGER REFERENCES person(id) ON DELETE CASCADE, \
       KontaktartCode INTEGER NOT NULL, \
       Kontakt VARCHAR(50), \
       Kontakt_Intern VARCHAR(50));""",
    """CREATE TABLE tier (id SERIAL PRIMARY KEY, \
       Tiername VARCHAR(30), \
       Tierart VARCHAR(30), \
       Rasse VARCHAR(30), \
       Farbe VARCHAR(30), \
       Viren VARCHAR(30), \
       Merkmal VARCHAR(50), \
       Geburtsdatum TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
       GeschlechtsartCode INTEGER NOT NULL, \
       Chip_Nummer VARCHAR(30), \
       EU_Passnummer VARCHAR(30), \
       Patient BOOLEAN NOT NULL DEFAULT true);""",
    """CREATE TABLE behandlung (id SERIAL PRIMARY KEY, \
       tier_id INTEGER REFERENCES tier(id) ON DELETE CASCADE, \
       Behandlungsdatum TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
       Gewicht_Kg VARCHAR(50), \
       Diagnose VARCHAR(1000), \
       Laborwerte1 VARCHAR(1000), \
       Laborwerte2 VARCHAR(1000), \
       Arzneien VARCHAR(255), \
       Arzneimittel VARCHAR(100), \
       Impfungen_Extern VARCHAR(100));""",
    """CREATE TABLE impfung (id SERIAL PRIMARY KEY, \
        behandlung_id INTEGER REFERENCES beahndlung(id) ON DELETE CASCADE, \
        ImpfungsartCode INTEGER NOT NULL);""",
    """CREATE TABLE behandlungsverlauf (id SERIAL PRIMARY KEY, \
       person_id INTEGER REFERENCES person(id) ON DELETE CASCADE, \
       tier_id INTEGER REFERENCES tier(id) ON DELETE CASCADE, \
       Datum TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
       Diagnose VARCHAR(255), \
       Behandlung VARCHAR(1000));""")
    """CREATE TABLE tierhaltung (id SERIAL PRIMARY KEY, \
       person_id INTEGER REFERENCES person(id) ON DELETE CASCADE, \
       tier_id INTEGER REFERENCES tier(id) ON DELETE CASCADE, \
       Anlagedatum TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);""")

