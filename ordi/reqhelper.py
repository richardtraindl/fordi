
from flask import request
from .values import *


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

def build_and_validate_tier(request):
    if(request.form.get('patient')):
        patient = "1"
    else:
        patient = "0"
    tier = cTier("", 
                 request.form['tiername'], 
                 request.form['tierart'], 
                 request.form['rasse'],
                 request.form['farbe'],
                 request.form['viren'],
                 request.form['merkmal'],
                 request.form['geburtsdatum'],
                 request.form['geschlechtscode'],
                 request.form['chip_nummer'],
                 request.form['eu_passnummer'],
                 patient)

    if(len(tier.tiername) == 0):
        return tier, "Tiername erforderlich. "
    if(len(tier.tierart) == 0):
        return tier, "Tierart erforderlich. "
    if(len(tier.geburtsdatum) == 0):
        return tier, "Geburtsdatum erforderlich. "
    return tier, ""


class cCalc:
    def __init__(self, brutto_summe=0, netto_summe=0, steuerbetrag_zwanzig=0, steuerbetrag_dreizehn=0, steuerbetrag_zehn=0):
        self.brutto_summe = brutto_summe
        self.netto_summe = netto_summe
        self.steuerbetrag_zwanzig = steuerbetrag_zwanzig
        self.steuerbetrag_dreizehn = steuerbetrag_dreizehn
        self.steuerbetrag_zehn = steuerbetrag_zehn


def calc_rechnung(rechnungszeilen):
    calc = cCalc()

    if(len(rechnungszeilen) == 0):
        return calc, "Mindestens eine Rechnungszeile erforderlich."

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


class cRechnung:
    def __init__(self, id="", 
                       person_id="", 
                       tier_id="", 
                       rechnungsjahr="", 
                       rechnungslfnr="",  
                       ausstellungsdatum="",
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


def build_and_validate_rechnung(request):
    rechnung = cRechnung()
    if(len(request.form['rechnungsjahr']) == 0):
        return rechnung, "Rechnungsjahr erforderlich."
    rechnung.rechnungsjahr = request.form['rechnungsjahr']
    
    if(len(request.form['rechnungslfnr']) == 0):
        return rechnung, "Rechnungslfnr erforderlich."
    rechnung.rechnungslfnr = request.form['rechnungslfnr']

    if(len(request.form['ausstellungsdatum']) == 0):
        rechnung.ausstellungsdatum = date.today().strftime("%Y-%m-%d")
    else:
        rechnung.ausstellungsdatum = request.form['ausstellungsdatum']    

    if(len(request.form['ausstellungsort']) == 0):
        rechnung.ausstellungsort = "Wien"
    else:
        rechnung.ausstellungsort = request.form['ausstellungsort']

    rechnung.diagnose = request.form['diagnose']
    rechnung.bezahlung = request.form['bezahlung']
    rechnung.brutto_summe = 0
    rechnung.netto_summe = 0
    rechnung.steuerbetrag_zwanzig = 0
    rechnung.steuerbetrag_dreizehn = 0
    rechnung.steuerbetrag_zehn = 0
    return rechnung, ""



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
    for idx in range(len(data[0])):
        rechnungszeile = cRechnungszeile(data[0][idx],
                                         "",
                                         data[1][idx],
                                         data[2][idx],
                                         data[3][idx],
                                         data[4][idx])
        if(len(rechnungszeile.id) == 0 and 
           (len(rechnungszeile.artikelcode) == 0 or rechnungszeile.artikelcode == "0") and
           len(rechnungszeile.artikel) == 0 and len(rechnungszeile.betrag) == 0):
            continue

        if(len(rechnungszeile.datum) == 0):
            rechnungszeile.datum = date.today().strftime("%Y-%m-%d")

        if(len(rechnungszeile.artikel) == 0):
            return rechnungszeilen, "Fehlende Artikelbeschreibung."

        rechnungszeilen.append(rechnungszeile)
    return rechnungszeilen, ""


               
