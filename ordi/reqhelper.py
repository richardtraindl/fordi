
from datetime import date

from flask import request
from . values import *
from . modeles import *


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
    if(flag):
        return tier, error
    else:
        return None, error


def fill_and_validate_person(request):
    try:
        person_id = int(request.form['person_id']
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
    if(flag):
        return person, error
    else:
        return None, error


def fill_and_validate_adresse(request):
    try:
        adresse_id = int(request.form['adresse_id']
    except:
        adresse_id = None

    try:
        person_id = int(request.form['person_id']
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
        kontakt1_id = int(request.form['kontakt1_id']
    except:
        kontakt1_id = None
    try:
        kontakt2_id = int(request.form['kontakt2_id']
    except:
        kontakt2_id = None

    try:
        person_id = int(request.form['person_id']
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
        behandlung_id = int(request.form['behandlung_id']
    except:
        behandlung_id = None

    try:
        tier_id = int(request.form['tier_id']
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
    if(flag):
        return behandlung, error
    else:
        return None, error


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
    if(flag):
        return rechnung, error
    else:
        return None, error


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
        req_rechnungszeile['datum'] = data[1][idx]
        req_rechnungszeile['artikelcode'] = data[2][idx]
        req_rechnungszeile['artikel'] = data[3][idx]
        req_rechnungszeile['betrag'] = data[4][idx]
        if(len(req_rechnungszeile['id']) == 0 and len(req_rechnungszeile['datum']) == 0 and
           (len(req_rechnungszeile['artikelcode']) == 0 or req_rechnungszeile['artikelcode'] == "0") and
           len(req_rechnungszeile['artikel']) == 0 and len(req_rechnungszeile['betrag']) == 0):
            continue
        req_rechnungszeilen.append(req_rechnungszeile)
    return req_rechnungszeilen

def fill_and_validate_rechnungszeilen(req_rechnungszeilen):
    rechnungszeilen = []
    for req_rechnungszeile in req_rechnungszeilen:
        rechnungszeile = cRechnungszeile(req_rechnungszeile['rechnungszeile_id'], 
                                         None, 
                                         req_rechnungszeile['datum'], 
                                         req_rechnungszeile['artikelcode'], 
                                         req_rechnungszeile['artikel'],
                                         req_rechnungszeile['betrag'])
        flag, error = rechnungszeile.validate()
        if(flag == False):
            rechnungszeilen.append(rechnungszeile)
        else:
            return None, error

    if(len(rechnungszeilen) > 0):
        return rechnungszeilen, error
    else:
        return None, "Mindestens eine Rechnungszeile erforderlich."

