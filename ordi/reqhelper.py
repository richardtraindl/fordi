
from datetime import date

from flask import request
from ordi.values import *
from ordi.models import *


def fill_and_validate_tier(tier, request):
    error = ""

    try:
        geschlechtscode = int(request.form['geschlechtscode'])
    except:
        geschlechtscode = GESCHLECHT['']

    if(len(request.form['geburtsdatum']) > 10):
        str_geburtsdatum = request.form['geburtsdatum'].split()[0]
    else:
        str_geburtsdatum = request.form['geburtsdatum']
    try:
        geburtsdatum = datetime.strptime(str_geburtsdatum, "%d.%m.%Y").date()
    except:
        geburtsdatum = None
        error = "Falsches Geburtsdatum. "

    if(request.form.get('patient')):
        patient = True
    else:
        patient = False

    if(tier == None):
        tier = Tier()
    tier.tiername=request.form['tiername']
    tier.tierart=request.form['tierart']
    tier.rasse=request.form['rasse']
    tier.farbe=request.form['farbe']
    tier.viren=request.form['viren']
    tier.merkmal=request.form['merkmal']
    tier.geburtsdatum=geburtsdatum
    tier.geschlechtscode=geschlechtscode
    tier.chip_nummer=request.form['chip_nummer']
    tier.eu_passnummer=request.form['eu_passnummer']
    tier.patient=patient

    if(len(tier.tiername) == 0):
        error += "Tiername fehlt. "
    if(len(tier.tierart) == 0):
        error += "Tierart fehlt. "
    return tier, error


def fill_and_validate_person(person, request):
    try:
        person_id = int(request.form['person_id'])
    except:
        person_id = None

    try:
        anredecode = int(request.form['anredecode'])
    except:
        anredecode = ANREDE['']

    if(request.form.get('kunde')):
        kunde = True
    else:
        kunde = False

    if(person == None):
        person = Person()
    person.anredecode=anredecode
    person.titel=request.form['titel']
    person.familienname=request.form['familienname']
    person.vorname=request.form['vorname']
    person.notiz=request.form['notiz']
    person.kunde=kunde
    person.adr_strasse=request.form['adr_strasse']
    person.adr_plz=request.form['adr_plz']
    person.adr_ort=request.form['adr_ort']
    person.kontakte=request.form['kontakte']

    error = ""
    if(len(person.familienname) == 0):
        error += "Familienname fehlt. "
    return person, error


"""def fill_and_validate_adresse(adresse, request):
    try:
        adresse_id = int(request.form['adresse_id'])
    except:
        adresse_id = None

    try:
        person_id = int(request.form['person_id'])
    except:
        person_id = None

    if(adresse == None):
        adresse = Adresse(person_id=person_id)
    adresse.strasse=request.form['strasse']
    adresse.postleitzahl=request.form['postleitzahl']
    adresse.ort=request.form['ort']

    return adresse, "" """


def fill_and_validate_behandlung(behandlung, req_behandlung):
    error = ""
    if(len(req_behandlung['behandlungsdatum']) > 10):
        str_behandlungsdatum = req_behandlung['behandlungsdatum'].split()[0]
    else:
        str_behandlungsdatum = req_behandlung['behandlungsdatum']
    try:
        behandlungsdatum = datetime.strptime(str_behandlungsdatum, "%d.%m.%Y")
    except:
        behandlungsdatum = None
        error += "Falsches Behandlungsdatum. "

    if(behandlung == None):
        behandlung = Behandlung()

    behandlung.behandlungsdatum=behandlungsdatum 
    behandlung.gewicht=req_behandlung['gewicht'] 
    behandlung.diagnose=req_behandlung['diagnose']
    behandlung.laborwerte1=req_behandlung['laborwerte1'] 
    behandlung.laborwerte2=req_behandlung['laborwerte2']
    behandlung.arzneien=req_behandlung['arzneien']
    behandlung.arzneimittel=req_behandlung['arzneimittel']
    behandlung.impfungen_extern=req_behandlung['impfungen_extern']

    return behandlung, error


def build_behandlungen(request):    
    data = (
        request.form.getlist('behandlung_id[]'),
        request.form.getlist('behandlungsdatum[]'),
        request.form.getlist('gewicht[]'),
        request.form.getlist('diagnose[]'),
        request.form.getlist('laborwerte1[]'),
        request.form.getlist('laborwerte2[]'),
        request.form.getlist('arzneien[]'),
        request.form.getlist('arzneimittel[]'),
        request.form.getlist('impfungen_extern[]')
    )
    req_behandlungen = []
    for idx in range(len(data[0])):
        req_behandlung = {}
        req_behandlung['behandlung_id'] = data[0][idx]
        req_behandlung['tier_id'] = ""
        req_behandlung['behandlungsdatum'] = data[1][idx]
        req_behandlung['gewicht'] = data[2][idx]
        req_behandlung['diagnose'] = data[3][idx]
        req_behandlung['laborwerte1'] = data[4][idx]
        req_behandlung['laborwerte2'] = data[5][idx]
        req_behandlung['arzneien'] = data[6][idx]
        req_behandlung['arzneimittel'] = data[7][idx]
        req_behandlung['impfungen_extern'] = data[8][idx]

        if(len(req_behandlung['behandlung_id']) == 0 and 
           len(req_behandlung['gewicht']) == 0 and
           len(req_behandlung['diagnose']) == 0 and
           len(req_behandlung['laborwerte1']) == 0 and
           len(req_behandlung['laborwerte2']) == 0 and
           len(req_behandlung['arzneien']) == 0 and
           len(req_behandlung['arzneimittel']) == 0 and
           len(req_behandlung['impfungen_extern']) == 0):
            continue

        req_behandlungen.append(req_behandlung)
    return req_behandlungen


def fill_and_validate_rechnung(rechnung, request):
    error = ""

    try:
        rechnungsjahr = int(request.form['rechnungsjahr'])
    except:
        rechnungsjahr = None

    try:
        rechnungslfnr = int(request.form['rechnungslfnr'])
    except:
        rechnungslfnr = None

    if(len(request.form['ausstellungsdatum']) > 10):
        str_ausstellungsdatum = request.form['ausstellungsdatum'].split()[0]
    else:
        str_ausstellungsdatum = request.form['ausstellungsdatum']
    try:
        ausstellungsdatum = datetime.strptime(str_ausstellungsdatum, "%d.%m.%Y")
    except:
        ausstellungsdatum = None
        error += "Falsches Ausstellungsdatum. "

    if(rechnung == None):
        rechnung = Rechnung()

    rechnung.rechnungsjahr=rechnungsjahr
    rechnung.rechnungslfnr=rechnungslfnr
    rechnung.ausstellungsdatum=ausstellungsdatum
    rechnung.ausstellungsort=request.form['ausstellungsort']
    rechnung.diagnose=request.form['diagnose']
    rechnung.bezahlung=request.form['bezahlung']
    rechnung.brutto_summe=0
    rechnung.netto_summe=0
    rechnung.steuerbetrag_zwanzig=0
    rechnung.steuerbetrag_dreizehn=0
    rechnung.steuerbetrag_zehn=0

    return rechnung, error


def build_rechnungszeilen(request):
    data = (
        request.form.getlist('rechnungszeile_id[]'),
        request.form.getlist('datum[]'),
        request.form.getlist('artikelcode[]'),
        request.form.getlist('artikel[]'),
        request.form.getlist('betrag[]')
    )
    req_rechnungszeilen = []
    for idx in range(len(data[0])):
        req_rechnungszeile = {}
        req_rechnungszeile['rechnungszeile_id'] = data[0][idx]
        req_rechnungszeile['rechnung_id'] = request.form['rechnung_id']
        req_rechnungszeile['datum'] = data[1][idx]
        req_rechnungszeile['artikelcode'] = data[2][idx]
        req_rechnungszeile['artikel'] = data[3][idx]
        req_rechnungszeile['betrag'] = data[4][idx]

        if(len(req_rechnungszeile['rechnungszeile_id']) == 0 and 
           req_rechnungszeile['artikelcode'] == "0" and
           len(req_rechnungszeile['artikel']) == 0 and 
           len(req_rechnungszeile['betrag']) == 0):
            continue

        req_rechnungszeilen.append(req_rechnungszeile)
    return req_rechnungszeilen

def fill_and_validate_rechnungszeile(rechnungszeile, req_rechnungszeile):
    error = ""

    if(len(req_rechnungszeile['datum']) > 10):
        str_datum = req_rechnungszeile['datum'].split()[0]
    else:
        str_datum = req_rechnungszeile['datum']
    try:
        datum = datetime.strptime(str_datum, "%d.%m.%Y")
    except:
        datum = None
        error += "Falsches Datum. "

    try:
        artikelcode = int(req_rechnungszeile['artikelcode'])
    except:
        artikelcode = 0
        error += "Falsche Artikelart. "

    if(len(req_rechnungszeile['artikel']) == 0):
        error += "Artikeldetail fehlt. "

    if(len(req_rechnungszeile['betrag']) == 0):
        betrag = None
        error += "Betrag fehlt. "
    else:
        try:
            betrag = float(req_rechnungszeile['betrag'].replace(",", "."))
        except:
            betrag = None
            error += "Betrag muss eine Zahl sein. "

    if(rechnungszeile == None):
        rechnungszeile = Rechnungszeile()

    rechnungszeile.datum=datum
    rechnungszeile.artikelcode=artikelcode
    rechnungszeile.artikel=req_rechnungszeile['artikel']
    rechnungszeile.betrag=betrag

    return rechnungszeile, error


def fill_and_validate_behandlungsverlauf(behandlungsverlauf, request):
    error = ""

    if(len(request.form['datum']) > 10):
        str_datum = request.form['datum'].split()[0]
    else:
        str_datum = request.form['datum']
    try:
        datum = datetime.strptime(str_datum, "%d.%m.%Y")
    except:
        datum = None
        error = "Falsches Datum. "

    if(behandlungsverlauf == None):
        behandlungsverlauf = Behandlungsverlauf()

    behandlungsverlauf.datum=datum
    behandlungsverlauf.diagnose=request.form['diagnose']
    behandlungsverlauf.behandlung=request.form['behandlung']

    return behandlungsverlauf, error

