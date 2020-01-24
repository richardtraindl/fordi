
from datetime import date

from flask import request
from ordi.values import *
from ordi.models import *


def fill_and_validate_tier(request):
    try:
        tier_id = int(request.form['tier_id'])
    except:
        tier_id = None

    if(request.form.get('patient')):
        patient = 1
    else:
        patient = 0

    tier = cTier(tier_id, 
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

    flag, error = tier.validate()
    return tier, error


def fill_and_validate_person(request):
    try:
        person_id = int(request.form['person_id'])
    except:
        person_id = None

    try:
        anredecode = int(request.form['anredecode'])
    except:
        anredecode = 0

    if(request.form.get('kunde')):
        kunde = 1
    else:
        kunde = 0

    person = cPerson(person_id, 
                     anredecode, 
                     request.form['titel'],
                     request.form['familienname'],
                     request.form['vorname'],
                     request.form['notiz'],
                     kunde)

    flag, error = person.validate()
    return person, error


def fill_and_validate_adresse(request):
    try:
        adresse_id = int(request.form['adresse_id'])
    except:
        adresse_id = None

    try:
        person_id = int(request.form['person_id'])
    except:
        person_id = None

    adresse = cAdresse(adresse_id, 
                       person_id,
                       request.form['strasse'],
                       request.form['postleitzahl'],
                       request.form['ort'])

    return adresse, ""


def fill_and_validate_kontakte(request):
    kontakte = []
    try:
        kontakt1_id = int(request.form['kontakt1_id'])
    except:
        kontakt1_id = None
    try:
        kontakt2_id = int(request.form['kontakt2_id'])
    except:
        kontakt2_id = None

    try:
        person_id = int(request.form['person_id'])
    except:
        person_id = None

    kontakte.append(cKontakt(kontakt1_id, 
                             person_id, 
                             "1", # fix 1 für Telefon
                             request.form['kontakt1'],
                            ""))
    kontakte.append(cKontakt(kontakt2_id, 
                             person_id, 
                             "1", # fix 1 für Telefon
                             request.form['kontakt2'],
                             ""))

    return kontakte, ""


def fill_and_validate_behandlung(request):
    try:
        behandlung_id = int(request.form['behandlung_id'])
    except:
        behandlung_id = None

    try:
        tier_id = int(request.form['tier_id'])
    except:
        tier_id = None

    behandlung = cBehandlung(behandlung_id, 
                             tier_id,
                             request.form['behandlungsdatum'], 
                             request.form['gewicht'],  
                             request.form['diagnose'],
                             request.form['laborwerte1'], 
                             request.form['laborwerte2'], 
                             request.form['arzneien'],
                             request.form['arzneimittel'], 
                             request.form['impfungen_extern'])

    flag, error = behandlung.validate()
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

def fill_and_validate_behandlungen(req_behandlungen):
    behandlungen = []
    return_error = ""

    for req_behandlung in req_behandlungen:
        try:
            behandlung_id = int(req_behandlung['behandlung_id'])
        except:
            behandlung_id = None
        try:
            tier_id = int(req_behandlung['tier_id'])
        except:
            tier_id = None

        if(len(req_behandlung['gewicht']) > 0):
            try:
                gewicht = float(req_behandlung['gewicht'].replace(",", "."))
            except:
                gewicht = None
                return_error = "Zahl für Gewicht erforderlich. "

        behandlung = cBehandlung(behandlung_id, 
                                 tier_id, 
                                 req_behandlung['behandlungsdatum'], 
                                 gewicht, 
                                 req_behandlung['diagnose'], 
                                 req_behandlung['laborwerte1'], 
                                 req_behandlung['laborwerte2'],
                                 req_behandlung['arzneien'],
                                 req_behandlung['arzneimittel'],
                                 req_behandlung['impfungen_extern'])

        flag, error = behandlung.validate()
        if(flag == False):
            return_error += error
        behandlungen.append(behandlung)

    return behandlungen, return_error


def fill_and_validate_rechnung(request):
    try:
        rechnung_id = int(request.form['rechnung_id'])
    except:
        rechnung_id = None

    try:
        person_id = int(request.form['person_id'])
    except:
        person_id = None

    try:
        tier_id = int(request.form['tier_id'])
    except:
        tier_id = None

    try:
        rechnungsjahr = int(request.form['rechnungsjahr'])
    except:
        rechnungsjahr = None

    try:
        rechnungslfnr = int(request.form['rechnungslfnr'])
    except:
        rechnungslfnr = None

    if(len(request.form['ausstellungsdatum']) == 0):
        ausstellungsdatum = date.today().strftime("%Y-%m-%d")
    else:
        ausstellungsdatum = request.form['ausstellungsdatum']

    if(len(request.form['ausstellungsort']) == 0):
        ausstellungsort = "Wien"
    else:
        ausstellungsort = request.form['ausstellungsort']

    rechnung = cRechnung(rechnung_id,
                         person_id,
                         tier_id,
                         rechnungsjahr,
                         rechnungslfnr,
                         ausstellungsdatum,
                         ausstellungsort,
                         request.form['diagnose'],
                         request.form['bezahlung'],
                         0,
                         0,
                         0,
                         0,
                         0)

    flag, error = rechnung.validate()
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
        req_rechnungszeile['rechnung_id'] = ""
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

def fill_and_validate_rechnungszeilen(req_rechnungszeilen):
    rechnungszeilen = []
    return_error = ""

    for req_rechnungszeile in req_rechnungszeilen:
        try:
            rechnungszeile_id = int(req_rechnungszeile['rechnungszeile_id'])
        except:
            rechnungszeile_id = None

        try:
            rechnung_id = int(req_rechnungszeile['rechnung_id'])
        except:
            rechnung_id = None

        try:
            artikelcode = int(req_rechnungszeile['artikelcode'])
        except:
            artikelcode = None          
            return_error = "Falsche Artikelbezeichnung. "

        try:
            betrag = float(req_rechnungszeile['betrag'].replace(",", "."))
        except:
            betrag = None
            return_error += "Betrag muss eine Zahl sein. "

        rechnungszeile = cRechnungszeile(rechnungszeile_id, 
                                         rechnung_id, 
                                         req_rechnungszeile['datum'], 
                                         artikelcode, 
                                         req_rechnungszeile['artikel'],
                                         betrag)

        flag, error = rechnungszeile.validate()
        if(flag == False):
            return_error = error
        rechnungszeilen.append(rechnungszeile)

    if(len(rechnungszeilen) == 0):
        return rechnungszeilen, return_error + "Mindestens eine Rechnungszeile erforderlich. "
    else:
        return rechnungszeilen, return_error

