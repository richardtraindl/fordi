
from .values import *

### Tier
class cTier:
    def __init__(self, 
                 id="", 
                 tiername="", 
                 tierart="", 
                 rasse="", 
                 farbe="", 
                 viren="", 
                 merkmal="", 
                 geburtsdatum="", 
                 geschlechtscode="",
                 chip_nummer ="",
                 eu_passnummer ="",
                 patient = ""):
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
            return False, "Tiername erforderlich."
        if(len(self.tierart) == 0):
            return False, "Tierart erforderlich."
        if(len(self.geburtsdatum) == 0):
            return False, "Geburtsdatum erforderlich."
        return True, ""
### Tier


### person
class cPerson:
    def __init__(self, 
                 id="", 
                 anredecode="", 
                 titel="", 
                 familienname="", 
                 vorname="", 
                 notiz="", 
                 kunde=""):
        self.id = id
        self.anredecode = anredecode
        self.titel = titel
        self.familienname = familienname
        self.vorname = vorname
        self.notiz = notiz
        self.kunde = kunde

    def validate(self):
        if(len(self.familienname) == 0):
            return False, "Familienname erforderlich."
        return True, ""
### person


### adresse
class cAdresse:
    def __init__(self, 
                 id="", 
                 person_id="", 
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
                 id="", 
                 person_id="", 
                 kontaktcode="1", # fix 1 für Telefon
                 kontakt="", 
                 kontakt_intern=""):
        self.id = id
        self.person_id = person_id
        self.kontaktcode = kontaktcode
        self.kontakt = kontakt
        bad_chars = [';', ':', '-', '/', ' ', '\n']
        self.kontakt_intern = ''.join(i for i in self.kontakt if not i in bad_chars)
        #self.kontakt_intern = kontakt_intern

    def validate(self):
        return True, ""
### kontakte


### rechnung
class cRechnung:
    def __init__(self, id=None, 
                       person_id=None,
                       tier_id=None, 
                       rechnungsjahr=None, 
                       rechnungslfnr=None,  
                       ausstellungsdatum=None,
                       ausstellungsort=None, 
                       diagnose=None, 
                       bezahlung=None,
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
        if(len(ausstellungsdatum) == 0):
            self.ausstellungsdatum = date.today().strftime("%Y-%m-%d")
        else:
            self.ausstellungsdatum = ausstellungsdatum
        if(len(ausstellungsort) == 0):
            self.ausstellungsort = "Wien"
        else:
            self.ausstellungsort = ausstellungsort
        self.diagnose = diagnose
        self.bezahlung = bezahlung
        self.brutto_summe = brutto_summe
        self.netto_summe = netto_summe
        self.steuerbetrag_zwanzig = steuerbetrag_zwanzig
        self.steuerbetrag_dreizehn = steuerbetrag_dreizehn
        self.steuerbetrag_zehn = steuerbetrag_zehn


    def validate(self):
        if(len(request.form['rechnungsjahr']) == 0):
            return False, "Rechnungsjahr erforderlich."
        if(len(request.form['rechnungslfnr']) == 0):
            return False, "Rechnungslfnr erforderlich."
        return True, ""


class cCalc:
    def __init__(self, brutto_summe=0, netto_summe=0, steuerbetrag_zwanzig=0, steuerbetrag_dreizehn=0, steuerbetrag_zehn=0):
        self.brutto_summe = brutto_summe
        self.netto_summe = netto_summe
        self.steuerbetrag_zwanzig = steuerbetrag_zwanzig
        self.steuerbetrag_dreizehn = steuerbetrag_dreizehn
        self.steuerbetrag_zehn = steuerbetrag_zehn


def calc_rechnung(rechnungszeilen):
    calc = cCalc()

    for rechnungszeile in rechnungszeilen:
        try:
            artikelcode = int(rechnungszeile.artikelcode)
            steuersatz = ARTIKEL_STEUER[artikelcode]
        except:
            return calc, "Falsche Artikelart."

        try:
            str_betrag = rechnungszeile.betrag.replace(",", ".")
            betrag = float(str_betrag)
            betrag = round(betrag, 2)
        except:
            return calc, "Betrag ist keine Zahl."

        calc.brutto_summe += betrag
        nettobetrag = round(betrag * 100 / (100 + steuersatz))
        if(steuersatz == 20):
            calc.steuerbetrag_zwanzig += (betrag - nettobetrag)
        elif(steuersatz == 13):
            calc.steuerbetrag_dreizehn += (betrag - nettobetrag)
        else: # steuersatz == 10
            calc.steuerbetrag_zehn += (betrag - nettobetrag)

    calc.netto_summe = calc.brutto_summe - (calc.steuerbetrag_zwanzig + calc.steuerbetrag_dreizehn + calc.steuerbetrag_zehn)
    return calc, ""




class cRechnungszeile:
    def __init__(self, id="", 
                       rechnung_id="", 
                       datum="", 
                       artikelcode="", 
                       artikel="",  
                       betrag=0):
        self.id = id
        self.rechnung_id = rechnung_id
        self.datum = datum
        self.artikelcode = artikelcode
        self.artikel = artikel
        self.betrag = betrag

def build_and_validate_rechnungszeilen(request):
    data = (
        request.form.getlist('rechnungszeile_id[]'),
        request.form.getlist('datum[]'),
        request.form.getlist('artikelcode[]'),
        request.form.getlist('artikel[]'),
        request.form.getlist('betrag[]')
    )
    rechnungszeilen = []
    error = ""
    for idx in range(len(data[0])):
        rechnungszeile = cRechnungszeile(data[0][idx],
                                         "",
                                         data[1][idx],
                                         data[2][idx],
                                         data[3][idx],
                                         data[4][idx])
        if(len(rechnungszeile.id) == 0 and len(rechnungszeile.datum) == 0 and
           (len(rechnungszeile.artikelcode) == 0 or rechnungszeile.artikelcode == "0") and
           len(rechnungszeile.artikel) == 0 and len(rechnungszeile.betrag) == 0):
            continue

        """if(len(rechnungszeile.datum) == 0):
            rechnungszeile.datum = date.today().strftime("%Y-%m-%d")"""

        if(len(rechnungszeile.artikel) == 0):
            error = "Fehlende Artikelbeschreibung."

        rechnungszeilen.append(rechnungszeile)

    if(len(rechnungszeilen) == 0):
        return rechnungszeilen, "Mindestens eine Rechnungszeile erforderlich."

    return rechnungszeilen, error
