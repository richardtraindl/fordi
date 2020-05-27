
from datetime import datetime
from . import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, nullable=False, unique=True)
    password = db.Column(db.String(256), index=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Tierhaltung(db.Model):
    __tablename__ = 'tierhaltung'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False, index=True)
    tier_id = db.Column(db.Integer, db.ForeignKey('tier.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    person = db.relationship("Person", uselist=False, back_populates="tierhaltung", lazy='immediate')
    tier = db.relationship("Tier", uselist=False, back_populates="tierhaltung", lazy='immediate')
    termine = db.relationship("Termin", cascade="all,delete", back_populates="tierhaltung", lazy='noload')

    def __repr__(self):
        return '<Tierhaltung %r>' % (self.id)


class Person(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
    anredecode = db.Column(db.Integer(), nullable=False)
    titel = db.Column(db.String(40))
    familienname = db.Column(db.String(40), nullable=False)
    vorname = db.Column(db.String(40))
    notiz = db.Column(db.String(200))
    kunde = db.Column(db.Boolean(), nullable=False, default=True)
    adr_strasse = db.Column(db.String(40))
    adr_plz = db.Column(db.String(40))
    adr_ort = db.Column(db.String(40))
    kontakte = db.Column(db.String(1000))
    tierhaltung = db.relationship("Tierhaltung", back_populates="person")

    def __repr__(self):
        return '<Person %r>' % (self.familienname)


class Tier(db.Model):
    __tablename__ = 'tier'

    id = db.Column(db.Integer, primary_key=True)
    tiername = db.Column(db.String(30), nullable=False)
    tierart = db.Column(db.String(30))
    rasse = db.Column(db.String(30))
    farbe = db.Column(db.String(30))
    viren = db.Column(db.String(30))
    merkmal = db.Column(db.String(50))
    geburtsdatum = db.Column(db.Date(), nullable=False)
    geschlechtscode = db.Column(db.Integer(), nullable=False)
    chip_nummer = db.Column(db.String(30))
    eu_passnummer = db.Column(db.String(30))
    patient = db.Column(db.Boolean(), nullable=False, default=True)
    tierhaltung = db.relationship("Tierhaltung", back_populates="tier")
    behandlungen = db.relationship("Behandlung", cascade="all,delete", back_populates="tier", lazy='noload')

    def __repr__(self):
        return '<Tier %r>' % (self.tiername)


class Behandlung(db.Model):
    __tablename__ = 'behandlung'

    id = db.Column(db.Integer, primary_key=True)
    tier_id = db.Column(db.Integer, db.ForeignKey('tier.id', ondelete='CASCADE'), nullable=False, index=True)
    datum = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    gewicht = db.Column(db.String(50))
    diagnose = db.Column(db.String(1000))
    laborwerte1 = db.Column(db.String(1000))
    laborwerte2 = db.Column(db.String(1000))
    arzneien = db.Column(db.String(256))
    arzneimittel = db.Column(db.String(100))
    impfungen_extern = db.Column(db.String(100))
    tier = db.relationship("Tier", back_populates="behandlungen")
    impfungen = db.relationship("Impfung", cascade="all,delete", back_populates="behandlung", lazy='joined')

    def __repr__(self):
        return '<Behandlung %r>' % (self.id)


class Impfung(db.Model):
    __tablename__ = 'impfung'

    id = db.Column(db.Integer, primary_key=True)
    behandlung_id = db.Column(db.Integer, db.ForeignKey('behandlung.id', ondelete='CASCADE'), nullable=False, index=True)
    impfungscode = db.Column(db.Integer(), nullable=False)
    behandlung = db.relationship("Behandlung", back_populates="impfungen")

    def __repr__(self):
        return '<Impfung %r>' % (self.impfungscode)


class Behandlungsverlauf(db.Model):
    __tablename__ = 'behandlungsverlauf'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE'), nullable=False, index=True)
    tier_id = db.Column(db.Integer, db.ForeignKey('tier.id', ondelete='CASCADE'), nullable=False, index=True)
    datum = db.Column(db.Date(), nullable=False, default=datetime.utcnow)
    diagnose = db.Column(db.String(256))
    behandlung = db.Column(db.String(1000))
    person = db.relationship("Person", uselist=False, lazy='immediate')
    tier = db.relationship("Tier", uselist=False, lazy='immediate')

    def __repr__(self):
        return '<Behandlungsverlauf %r>' % (self.tiername)


class Rechnung(db.Model):
    __tablename__ = 'rechnung'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE'), nullable=False, index=True)
    tier_id = db.Column(db.Integer, db.ForeignKey('tier.id', ondelete='CASCADE'), nullable=False, index=True)
    jahr = db.Column(db.Integer(), nullable=False)
    lfnr = db.Column(db.Integer(), nullable=False)
    datum = db.Column(db.Date(), nullable=False, default=datetime.utcnow)
    ort = db.Column(db.String(256))
    diagnose = db.Column(db.String(256))
    bezahlung = db.Column(db.String(256))
    brutto_summe = db.Column(db.Numeric(8, 2))
    netto_summe = db.Column(db.Numeric(8, 2))
    steuerbetrag_zwanzig = db.Column(db.Numeric(8, 2))
    steuerbetrag_dreizehn = db.Column(db.Numeric(8, 2))
    steuerbetrag_zehn = db.Column(db.Numeric(8, 2))
    person = db.relationship("Person", uselist=False, lazy='immediate')
    tier = db.relationship("Tier", uselist=False, lazy='immediate')
    rechnungszeilen = db.relationship("Rechnungszeile", cascade="all,delete", back_populates="rechnung", lazy='noload')

    def __repr__(self):
        return '<Rechnung %r>' % (self.id)


class Rechnungszeile(db.Model):
    __tablename__ = 'rechnungszeile'

    id = db.Column(db.Integer, primary_key=True)
    rechnung_id = db.Column(db.Integer, db.ForeignKey('rechnung.id', ondelete='CASCADE'), nullable=False, index=True)
    datum = db.Column(db.Date(), nullable=False, default=datetime.utcnow)
    artikelcode = db.Column(db.Integer(), nullable=False)
    artikel = db.Column(db.String(256))
    betrag = db.Column(db.Numeric(8, 2))
    rechnung = db.relationship("Rechnung", back_populates="rechnungszeilen")

    def __repr__(self):
        return '<rechnungszeile %r>' % (self.id)


class Termin(db.Model):
    __tablename__ = 'termin'

    id = db.Column(db.Integer, primary_key=True)
    tierhaltung_id = db.Column(db.Integer, db.ForeignKey('tierhaltung.id'), index=True)
    autor = db.Column(db.String(30))
    beginn = db.Column(db.DateTime(timezone=True), nullable=False)
    ende = db.Column(db.DateTime(timezone=True), nullable=False)
    thema = db.Column(db.String(50), nullable=False)
    tierhaltung = db.relationship("Tierhaltung", back_populates="termine")

    def __repr__(self):
        return '<termin %r>' % (self.id)
