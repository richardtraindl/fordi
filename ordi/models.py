
from app import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, nullable=False, unique=True)
    password = db.Column(db.String(256), index=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Person(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
    anredecode = db.Column(db.Integer(), nullable=False)
    titel = db.Column(db.String(40))
    familienname = db.Column(db.String(40), nullable=False)
    vorname = db.Column(db.String(40))
    notiz = db.Column(db.String(200))
    kunde = db.Column(db.Boolean(), nullable=False, default=True)

    def __repr__(self):
        return '<Person %r>' % (self.familienname)


class Adresse(db.Model):
    __tablename__ = 'adresse'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    strasse = db.Column(db.String(40))
    postleitzahl = db.Column(db.String(40))
    ort = db.Column(db.String(40))

    def __repr__(self):
        return '<Adresse %r>' % (self.strasse)

class Kontakt(db.Model):
    __tablename__ = 'kontakt'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    kontaktcode = db.Column(db.Integer(), nullable=False)
    kontakt = db.Column(db.String(50))
    kontakt_intern = db.Column(db.String(50))

    def __repr__(self):
        return '<Kontakt %r>' % (self.kontakt)


class Tier(db.Model):
    __tablename__ = 'tier'

    id = db.Column(db.Integer, primary_key=True)
    tiername = db.Column(db.String(30), nullable=False)
    tierart = db.Column(db.String(30))
    rasse = db.Column(db.String(30), nullable=False)
    farbe = db.Column(db.String(30))
    viren = db.Column(db.String(30))
    merkmal = db.Column(db.String(50))
    geburtsdatum = db.Column(db.DateTime(), nullable=False)
    geschlechtscode = db.Column(db.Integer(), nullable=False)
    chip_nummer = db.Column(db.String(30))
    eu_passnummer = db.Column(db.String(30))
    patient = db.Column(db.Boolean(), nullable=False, default=True)

    def __repr__(self):
        return '<Tier %r>' % (self.tiername)


class Behandlung(db.Model):
    __tablename__ = 'behandlung'

    id = db.Column(db.Integer, primary_key=True)
    tier_id = db.Column(db.Integer, db.ForeignKey('tier.id'))
    behandlungsdatum = db.Column(db.DateTime(), nullable=False)
    gewicht = db.Column(db.String(50))
    diagnose = db.Column(db.String(1000))
    laborwerte1 = db.Column(db.String(1000))
    laborwerte2 = db.Column(db.String(1000))
    arzneien = db.Column(db.String(256))
    arzneimittel = db.Column(db.String(100))
    impfungen_extern = db.Column(db.String(100))

    def __repr__(self):
        return '<Behandlung %r>' % (self.diagnose)


class Impfung(db.Model):
    __tablename__ = 'impfung'

    id = db.Column(db.Integer, primary_key=True)
    behandlung_id = db.Column(db.Integer, db.ForeignKey('behandlung.id'))
    impfungscode = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return '<Impfung %r>' % (self.impfungscode)


class Tierhaltung(db.Model):
    __tablename__ = 'tierhaltung'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    tier_id = db.Column(db.Integer, db.ForeignKey('tier.id'))
    anlagezeit = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return '<Tierhaltung %r>' % (self.anlagezeit)

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
       artikelcode INTEGER NOT NULL, \
       artikel VARCHAR(255), \
       betrag DECIMAL(10,2) NOT NULL);""")
