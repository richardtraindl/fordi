
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
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE'))
    strasse = db.Column(db.String(40))
    postleitzahl = db.Column(db.String(40))
    ort = db.Column(db.String(40))

    def __repr__(self):
        return '<Adresse %r>' % (self.strasse)

class Kontakt(db.Model):
    __tablename__ = 'kontakt'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE'))
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
    rasse = db.Column(db.String(30))
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
    tier_id = db.Column(db.Integer, db.ForeignKey('tier.id', ondelete='CASCADE'))
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
    behandlung_id = db.Column(db.Integer, db.ForeignKey('behandlung.id', ondelete='CASCADE'))
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


class Behandlungsverlauf(db.Model):
    __tablename__ = 'behandlungsverlauf'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE'))
    tier_id = db.Column(db.Integer, db.ForeignKey('tier.id', ondelete='CASCADE'))
    datum = db.Column(db.DateTime(), nullable=False)
    diagnose = db.Column(db.String(256))
    behandlung = db.Column(db.String(1000))

    def __repr__(self):
        return '<Behandlungsverlauf %r>' % (self.tiername)


class Rechnung(db.Model):
    __tablename__ = 'rechnung'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE'))
    tier_id = db.Column(db.Integer, db.ForeignKey('tier.id', ondelete='CASCADE'))
    rechnungsjahr = db.Column(db.Integer(), nullable=False)
    rechnungslfnr = db.Column(db.Integer(), nullable=False)
    ausstellungsdatum = db.Column(db.DateTime(), nullable=False)
    ausstellungsort = db.Column(db.String(256))
    diagnose = db.Column(db.String(256))
    bezahlung = db.Column(db.String(256))
    brutto_summe = db.Column(db.Numeric(8, 2))
    netto_summe = db.Column(db.Numeric(8, 2))
    steuerbetrag_zwanzig = db.Column(db.Numeric(8, 2))
    steuerbetrag_dreizehn = db.Column(db.Numeric(8, 2))
    steuerbetrag_zehn = db.Column(db.Numeric(8, 2))

    def __repr__(self):
        return '<Rechnung %r>' % (self.id)


   class Rechnungszeile(db.Model):
    __tablename__ = 'rechnungszeile'

    id = db.Column(db.Integer, primary_key=True)
    rechnung_id = db.Column(db.Integer, db.ForeignKey(rechnung.id', ondelete='CASCADE'))
    datum = db.Column(db.DateTime(), nullable=False)
    artikelcode = db.Column(db.Integer(), nullable=False)
    artikel = db.Column(db.String(256))
    betrag = db.Column(db.Numeric(8, 2))

    def __repr__(self):
        return '<rechnungszeile %r>' % (self.id)

