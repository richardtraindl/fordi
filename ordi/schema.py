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
    """CREATE TABLE tier (id SERIAL PRIMARY KEY, \
       Tiername 
       AnredeartCode INTEGER NOT NULL, \
       Titel VARCHAR(40), \
       Familienname VARCHAR(40), \
       Vorname VARCHAR(40), \
       Notiz VARCHAR(200), \
       Kunde BOOLEAN NOT NULL DEFAULT true);""",

    """CREATE TABLE owner (id SERIAL PRIMARY KEY, \
       auth_user_id INTEGER REFERENCES auth_user(id), \
       auth_guest_id INTEGER REFERENCES auth_user(id), \
       status INTEGER NOT NULL DEFAULT 0, \
       level INTEGER NOT NULL DEFAULT 1, \
       created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
       board VARCHAR(64) NOT NULL DEFAULT '42356324111111110000000000000000000000000000000099999999CABDEBAC');""",

    """CREATE TABLE move (id SERIAL PRIMARY KEY, \
        match_id INTEGER REFERENCES match(id) ON DELETE CASCADE, \
        prevfields VARCHAR(64) NOT NULL, \
        src VARCHAR(2) NOT NULL, \
        dst VARCHAR(2) NOT NULL, \
        prompiece VARCHAR(3));""",
    """CREATE TABLE comment (id SERIAL PRIMARY KEY, \
       match_id INTEGER REFERENCES match(id) ON DELETE CASCADE, \
       created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, \
       text VARCHAR(256) NOT NULL);""")
       
