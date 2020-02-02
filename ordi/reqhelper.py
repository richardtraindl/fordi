
from datetime import date

from flask import request
from ordi.values import *
from ordi.models import *


def fill_and_validate_tier(tier, request):
    try:
        geschlechtscode = int(request.form['geschlechtscode'])
    except:
        geschlechtscode = GESCHLECHT['']

    if(len(request.form['geburtsdatum']) > 10):
        str_geburtsdatum = request.form['geburtsdatum'].split()[0]
        geburtsdatum = datetime.strptime(str_geburtsdatum, "%Y-%m-%d")
    else:
        geburtsdatum = datetime.strptime(request.form['geburtsdatum'], "%Y-%m-%d")

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

    error = ""
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

    error = ""
    if(len(person.familienname) == 0):
        error += "Familienname fehlt. "
    return person, error


def fill_and_validate_adresse(adresse, request):
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

    return adresse, ""


def fill_and_validate_kontakte(kontakte, request):
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
        
    if(len(request.form['kontakt1']) > 0):
        bad_chars = [';', ':', '-', '/', ' ', '\n']
        kontakt1_intern = ''.join(i for i in request.form['kontakt1'] if not i in bad_chars)
    else:
        kontakt1_intern = ""

    if(len(request.form['kontakt2']) > 0):
        bad_chars = [';', ':', '-', '/', ' ', '\n']
        kontakt2_intern = ''.join(i for i in request.form['kontakt2'] if not i in bad_chars)
    else:
        kontakt2_intern = ""

    if(len(kontakte) == 0):
        kontakte.append(Kontakt(person_id=person_id))
    kontakte[0].kontaktcode=1 # fix 1 für Telefon
    kontakte[0].kontakt=request.form['kontakt1']
    kontakte[0].kontakt_intern=kontakt1_intern

    if(len(kontakte) < 2):
        kontakte.append(Kontakt(person_id=person_id))
    kontakte[1].kontaktcode=1 # fix 1 für Telefon
    kontakte[1].kontakt=request.form['kontakt2']
    kontakte[1].kontakt_intern=kontakt2_intern

    return kontakte, ""


def fill_and_validate_behandlung(behandlung, request):
    if(len(request.form['behandlungsdatum']) > 10):
        str_behandlungsdatum = request.form['behandlungsdatum'].split()[0]
        behandlungsdatum = datetime.strptime(str_behandlungsdatum, "%Y-%m-%d")
    else:
        behandlungsdatum = datetime.strptime(request.form['behandlungsdatum'], "%Y-%m-%d")

    behandlung = Behandlung(behandlungsdatum=behandlungsdatum, 
                            gewicht=request.form['gewicht'],  
                            diagnose=request.form['diagnose'],
                            laborwerte1=request.form['laborwerte1'], 
                            laborwerte2=request.form['laborwerte2'], 
                            arzneien=request.form['arzneien'],
                            arzneimittel=request.form['arzneimittel'], 
                            impfungen_extern=request.form['impfungen_extern'])
    return behandlung, ""


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

        tier_id = None

        if(len(req_behandlung['behandlungsdatum']) > 10):
            str_behandlungsdatum = req_behandlung['behandlungsdatum'].split()[0]
            behandlungsdatum = datetime.strptime(str_behandlungsdatum, "%Y-%m-%d")
        else:
            behandlungsdatum = datetime.strptime(req_behandlung['behandlungsdatum'], "%Y-%m-%d")

        if(len(req_behandlung['gewicht']) == 0):
            gewicht = None
        else:
            try:
                gewicht = float(req_behandlung['gewicht'].replace(",", "."))
            except:
                gewicht = None
                return_error += "Gewicht muss eine Zahl sein. "

        behandlung = Behandlung(id=behandlung_id, 
                                tier_id=tier_id, 
                                behandlungsdatum=behandlungsdatum, 
                                gewicht=gewicht, 
                                diagnose=req_behandlung['diagnose'], 
                                laborwerte1=req_behandlung['laborwerte1'], 
                                laborwerte2=req_behandlung['laborwerte2'],
                                arzneien=req_behandlung['arzneien'],
                                arzneimittel=req_behandlung['arzneimittel'],
                                impfungen_extern=req_behandlung['impfungen_extern'])

        #flag, error = behandlung.validate()
        #if(flag == False and len(return_error) == 0):
        #    return_error = error
        behandlungen.append(behandlung)

    return behandlungen, return_error


def fill_and_validate_rechnung(request):
    try:
        rechnung_id = int(request.form['rechnung_id'])
    except:
        rechnung_id = None

    person_id = None
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

    crechnung = cRechnung(rechnung_id,
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

    flag, error = crechnung.validate()
    return crechnung, error


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

        if(len(req_rechnungszeile['datum']) == 0):
            return_error += "Datum fehlt. "

        try:
            artikelcode = int(req_rechnungszeile['artikelcode'])
        except:
            artikelcode = 0
            return_error += "Falsche Artikelart. "

        if(len(req_rechnungszeile['artikel']) == 0):
            return_error += "Artikeldetail fehlt. "

        if(len(req_rechnungszeile['betrag']) == 0):
            betrag = None
            return_error += "Betrag fehlt. "
        else:
            try:
                betrag = float(req_rechnungszeile['betrag'].replace(",", "."))
            except:
                betrag = None
                return_error += "Betrag muss eine Zahl sein. "

        crechnungszeile = cRechnungszeile(rechnungszeile_id, 
                                          rechnung_id, 
                                          req_rechnungszeile['datum'], 
                                          artikelcode, 
                                          req_rechnungszeile['artikel'],
                                          betrag)

        flag, error = crechnungszeile.validate()
        if(flag == False and len(return_error) == 0):
            return_error = error
        rechnungszeilen.append(crechnungszeile)

    if(len(rechnungszeilen) == 0):
        return rechnungszeilen, return_error + "Mindestens eine Rechnungszeile erforderlich. "
    else:
        return rechnungszeilen, return_error


def fill_and_validate_behandlungsverlauf(request):
    try:
        behandlungsverlauf_id = int(request.form['behandlungsverlauf_id'])
    except:
        behandlungsverlauf_id = None

    person_id = None
    tier_id = None

    cbehandlungsverlauf = cBehandlungsverlauf(behandlungsverlauf_id,
                                              person_id,
                                              tier_id,
                                              request.form['datum'],
                                              request.form['diagnose'],
                                              request.form['behandlung'])

    flag, error = cbehandlungsverlauf.validate()
    return cbehandlungsverlauf, error

