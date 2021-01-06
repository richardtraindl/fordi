
from datetime import datetime

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
    error = ""

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

    if(len(person.familienname) == 0):
        error += "Familienname fehlt. "
    return person, error


def build_behandlungen(request):    
    data = (
        request.form.getlist('behandlung_id[]'),
        request.form.getlist('datum[]'),
        request.form.getlist('gewicht[]'),
        request.form.getlist('diagnose[]'),
        request.form.getlist('laborwerte1[]'),
        request.form.getlist('laborwerte2[]'),
        request.form.getlist('arzneien[]'),
        request.form.getlist('arzneimittel[]'),
        request.form.getlist('impfungen[]')
    )
    reqbehandlungen = []
    for idx in range(len(data[0])):
        reqbehandlung = {}
        reqbehandlung['behandlung_id'] = data[0][idx]
        reqbehandlung['tier_id'] = ""
        reqbehandlung['datum'] = data[1][idx]
        reqbehandlung['gewicht'] = data[2][idx]
        reqbehandlung['diagnose'] = data[3][idx]
        reqbehandlung['laborwerte1'] = data[4][idx]
        reqbehandlung['laborwerte2'] = data[5][idx]
        reqbehandlung['arzneien'] = data[6][idx]
        reqbehandlung['arzneimittel'] = data[7][idx]
        reqbehandlung['impfungen'] = data[8][idx]

        if(len(reqbehandlung['behandlung_id']) == 0 and 
           len(reqbehandlung['gewicht']) == 0 and
           len(reqbehandlung['diagnose']) == 0 and
           len(reqbehandlung['laborwerte1']) == 0 and
           len(reqbehandlung['laborwerte2']) == 0 and
           len(reqbehandlung['arzneien']) == 0 and
           len(reqbehandlung['arzneimittel']) == 0 and
           len(reqbehandlung['impfungen']) == 0):
            continue

        reqbehandlungen.append(reqbehandlung)
    return reqbehandlungen


def fill_and_validate_behandlung(behandlung, reqbehandlung):
    error = ""

    if(len(reqbehandlung['datum']) > 10):
        str_datum = reqbehandlung['datum'].split()[0]
    else:
        str_datum = reqbehandlung['datum']
    try:
        datum = datetime.strptime(str_datum, "%d.%m.%Y")
    except:
        error += "Falsches Behandlungsdatum. "
        datum = None

    if(behandlung == None):
        behandlung = Behandlung()

    behandlung.datum=datum 
    behandlung.gewicht=reqbehandlung['gewicht'] 
    behandlung.diagnose=reqbehandlung['diagnose']
    behandlung.laborwerte1=reqbehandlung['laborwerte1'] 
    behandlung.laborwerte2=reqbehandlung['laborwerte2']
    behandlung.arzneien=reqbehandlung['arzneien']
    behandlung.arzneimittel=reqbehandlung['arzneimittel']

    return behandlung, reqbehandlung['impfungen'], error


def fill_and_validate_rechnung(rechnung, request):
    error = ""

    try:
        jahr = int(request.form['jahr'])
    except:
        jahr = None
        error += "Jahr fehlt oder ungültig. "
    try:
        lfnr = int(request.form['lfnr'])
    except:
        lfnr = None
        error += "Laufnummer fehlt oder ungültig. "

    if(len(request.form['datum']) > 10):
        str_datum = request.form['datum'].split()[0]
    else:
        str_datum = request.form['datum']
    try:
        datum = datetime.strptime(str_datum, "%d.%m.%Y")
    except:
        datum = None
        error += "Falsches Ausstellungsdatum. "

    if(rechnung == None):
        rechnung = Rechnung()

    rechnung.jahr=jahr
    rechnung.lfnr=lfnr
    rechnung.datum=datum
    rechnung.ort=request.form['ort']
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
        request.form.getlist('touched[]'),
        request.form.getlist('datum[]'),
        request.form.getlist('artikelcode[]'),
        request.form.getlist('artikel[]'),
        request.form.getlist('betrag[]')
    )
    req_rechnungszeilen = []
    for idx in range(len(data[0])):
        req_rechnungszeile = {}
        req_rechnungszeile['rechnungszeile_id'] = data[0][idx]
        req_rechnungszeile['touched'] = data[1][idx]
        req_rechnungszeile['datum'] = data[2][idx]
        req_rechnungszeile['artikelcode'] = data[3][idx]
        req_rechnungszeile['artikel'] = data[4][idx]
        req_rechnungszeile['betrag'] = data[5][idx]

        if(len(req_rechnungszeile['rechnungszeile_id']) == 0 and 
           req_rechnungszeile['artikelcode'] == "0" and
           len(req_rechnungszeile['artikel']) == 0 and 
           len(req_rechnungszeile['betrag']) == 0):
            continue

        req_rechnungszeilen.append(req_rechnungszeile)
    return req_rechnungszeilen


def fill_and_validate_rechnungszeile(rechnung, rechnungszeile, req_rechnungszeile):
    error = ""

    try:
        rechnungszeile_id = int(req_rechnungszeile['rechnungszeile_id'])
    except:
        rechnungszeile_id = None

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
        artikelcode = None
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

    if(rechnungszeile_id):
        rechnungszeile.id=rechnungszeile_id
    if(rechnung and rechnung.id):
        rechnungszeile.rechnung_id=rechnung.id
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
        error += "Falsches Datum. "

    if(behandlungsverlauf == None):
        behandlungsverlauf = Behandlungsverlauf()

    behandlungsverlauf.datum=datum
    behandlungsverlauf.diagnose=request.form['diagnose']
    behandlungsverlauf.behandlung=request.form['behandlung']

    return behandlungsverlauf, error

