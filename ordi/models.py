
import re
from datetime import date
from .values import *


### Tier
class cTier:
    def __init__(self, 
                 id=None, 
                 tiername="", 
                 tierart="", 
                 rasse="", 
                 farbe="", 
                 viren="", 
                 merkmal="", 
                 geburtsdatum=None, 
                 geschlechtscode=None,
                 chip_nummer="",
                 eu_passnummer=",
                 patient=1):
        self.id = id
        self.tiername = tiername
        self.tierart = tierart
        self.rasse = rasse
        self.farbe = farbe
        self.viren = viren
        self.merkmal = merkmal
        self.geburtsdatum = geburtsdatum
        self.geschlechtscode = geschlechtscode
        self.chip_nummer = chip_nummer
        self.eu_passnummer = eu_passnummer
        self.patient = patient

    def validate(self):
        if(len(self.tiername) == 0):
            return False, "Tiername fehlt. "
        if(len(self.tierart) == 0):
            return False, "Tierart fehlt. "
        if(self.geburtsdatum == None):
            return False, "Geburtsdatum fehlt. "
        return True, ""
### Tier


### person
class cPerson:
    def __init__(self, 
                 id=None, 
                 anredecode=0, 
                 titel="", 
                 familienname="", 
                 vorname="", 
                 notiz="", 
                 kunde=1):
        self.id = id
        self.anredecode = anredecode
        self.titel = titel
        self.familienname = familienname
        self.vorname = vorname
        self.notiz = notiz
        self.kunde = kunde
        self.adresse = None
        self.kontakte = []

    def validate(self):
        if(len(self.familienname) == 0):
            return False, "Familienname fehlt. "
        return True, ""
### person


### adresse
class cAdresse:
    def __init__(self, 
                 id=None, 
                 person_id=None, 
                 strasse="", 
                 postleitzahl="", 
                 ort=""):
        self.id = id
        self.person_id = person_id
        self.strasse = strasse
        self.postleitzahl = postleitzahl
        self.ort = ort

    def validate(self):
        return True, ""
### adresse


### kontakte
class cKontakt:
    def __init__(self, 
                 id=None, 
                 person_id=None, 
                 kontaktcode=1, # fix 1 für Telefon
                 kontakt="", 
                 kontakt_intern=""):
        self.id = id
        self.person_id = person_id
        self.kontaktcode = kontaktcode
        self.kontakt = kontakt
        bad_chars = [';', ':', '-', '/', ' ', '\n']
        self.kontakt_intern = ''.join(i for i in self.kontakt if not i in bad_chars)

    def validate(self):
        return True, ""
### kontakte


### behandlung
class cBehandlung:
    def __init__(self, 
                 id=None, 
                 tier_id=None,
                 behandlungsdatum=None, 
                 gewicht=None,  
                 diagnose="",
                 laborwerte1="", 
                 laborwerte2="", 
                 arzneien="",
                 arzneimittel="", 
                 impfungen_extern=""):
        self.id = id
        self.tier_id = tier_id
        self.behandlungsdatum = behandlungsdatum
        self.gewicht = gewicht
        self.diagnose = diagnose
        self.laborwerte1 = laborwerte1
        self.laborwerte2 = laborwerte2
        self.arzneien = arzneien
        self.arzneimittel = arzneimittel
        self.impfungen_extern = impfungen_extern
        self.impfungen = []

    def validate(self):
        if(self.behandlungsdatum == None):
            return False, "Behandlungsdatum fehlt. "
        return True, ""
### behandlung


### impfung
class CImpfung:
    def __init__(self, id=None, behandlung_id=None, impfungscode=None):
        self.id = id
        self.behandlung_id = behandlung_id
        self.impfungscode = impfungscode

    def validate(self):
        if(self.impfungscode == None):
            return False, "Impfungscode fehlt. "
        return True, ""
### impfung


### rechnung
class cRechnung:
    def __init__(self, id=None, 
                       person_id=None,
                       tier_id=None, 
                       rechnungsjahr=None, 
                       rechnungslfnr=None,  
                       ausstellungsdatum=None,
                       ausstellungsort="", 
                       diagnose="", 
                       bezahlung="",
                       brutto_summe=0, 
                       netto_summe=0, 
                       steuerbetrag_zwanzig=0, 
                       steuerbetrag_dreizehn=0, 
                       steuerbetrag_zehn=0):
        self.id = id
        self.person_id = person_id
        self.tier_id = tier_id
        self.rechnungsjahr = rechnungsjahr
        self.rechnungslfnr = rechnungslfnr
        self.ausstellungsdatum = ausstellungsdatum
        self.ausstellungsort = ausstellungsort
        self.diagnose = diagnose
        self.bezahlung = bezahlung
        self.brutto_summe = brutto_summe
        self.netto_summe = netto_summe
        self.steuerbetrag_zwanzig = steuerbetrag_zwanzig
        self.steuerbetrag_dreizehn = steuerbetrag_dreizehn
        self.steuerbetrag_zehn = steuerbetrag_zehn
        self.rechnungszeilen = []

    def validate(self):
        if(self.rechnungsjahr == None):
            return False, "Rechnungsjahr fehlt. "
        if(self.rechnungslfnr == None):
            return False, "Rechnungslfnr fehlt. "
        if(self.ausstellungsdatum == None):
            return False, "Ausstellungsdatum fehlt. "
        if(len(self.ausstellungsort) == 0):
            return False, "Ausstellungsort fehlt. "
        return True, ""

    def calc(self):
        self.brutto_summe = 0
        self.steuerbetrag_zwanzig = 0
        self.steuerbetrag_dreizehn = 0
        self.steuerbetrag_zehn = 0

        for rechnungszeile in self.rechnungszeilen:
            try:
                artikelcode = int(rechnungszeile.artikelcode)
                steuersatz = ARTIKEL_STEUER[artikelcode]
            except:
                return False, "Falsche Artikelart."
            try:
                str_betrag = rechnungszeile.betrag.replace(",", ".")
                betrag = float(str_betrag)
                betrag = round(betrag, 2)
            except:
                return False, "Betrag ist keine Zahl."

            self.brutto_summe += betrag
            nettobetrag = round(betrag * 100 / (100 + steuersatz))
            if(steuersatz == 20):
                self.steuerbetrag_zwanzig += (betrag - nettobetrag)
            elif(steuersatz == 13):
                self.steuerbetrag_dreizehn += (betrag - nettobetrag)
            else: # steuersatz == 10
                self.steuerbetrag_zehn += (betrag - nettobetrag)

        self.netto_summe = self.brutto_summe - (self.steuerbetrag_zwanzig + self.steuerbetrag_dreizehn + self.steuerbetrag_zehn)
        return True, ""
### rechnung


### rechnungszeile
class cRechnungszeile:
    def __init__(self, 
                 id=None, 
                 rechnung_id=None, 
                 datum=None, 
                 artikelcode=0, 
                 artikel="",
                 betrag=None):
        self.id = id
        self.rechnung_id = rechnung_id
        self.datum = datum
        self.artikelcode = artikelcode
        self.artikel = artikel
        self.betrag = betrag

    def validate(self):
        if(self.artikelcode == None or self.artikelcode == 0):
            return False, "Artikelart fehlt. "
        if(len(self.artikel) == 0):
            return False, "Artikelbeschreibung fehlt. "
        if(self.betrag == None):
            return False, "Artikelbetrag fehlt. "
        return True, ""
### rechnungszeile

