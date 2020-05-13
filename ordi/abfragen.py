

from datetime import date, datetime
import os

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, send_file
from werkzeug.exceptions import abort
from sqlalchemy import func, distinct, or_, and_

from . import db
from ordi.auth import login_required
from ordi.models import *
from ordi.reqhelper import *
from ordi.values import *
from ordi.createpdf import *

bp = Blueprint('abfrage', __name__, url_prefix='/abfrage')


def dl_etiketten(abfrage, tierhaltungen):
    html = render_template('abfragen/print_etiketten.html', tierhaltungen=tierhaltungen)
    filename = abfrage + "_etiketten.pdf"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)

    html2pdf_etiketten(html, path_and_filename)

    return path_and_filename


def dl_excel(abfrage, tierhaltungen):
    filename = abfrage + ".xlsx"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)

    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws['A1'] = 42
    ws.append([1, 2, 3])
    ws['A2'] = datetime.now()
    ws['A3'] = 44
    wb.save(path_and_filename)

    return path_and_filename


def str_to_date(str_date):
    datum = None
    error = ""
    if(len(str_date) != 10):
        error += "Falsche Datumslänge. "

    try:
        datum = datetime.strptime(str_date, '%Y-%m-%d').date()
    except:
        error += "Fehler bei Datum. "

    return datum, error


lst_abfragen = ["", "Adresse", "Arzneien", "Arzneimittel", "Behandlung", \
                "Chipnummer", "Diagnose", "EU-Passnummer", "Finanzamt", \
                "Impfung", "Kontakte", "Merkmal", "Postleitzahl", "Rasse", "Tierart"]

@bp.route('/index', methods=('GET', 'POST'))
@login_required
def index():
    output = ""

    if(request.method == 'POST'):
        abfrage = request.form['abfrage']

        kriterium1 = request.form['kriterium1']
        try:
            kriterium2 = request.form['kriterium2']
        except:
            kriterium2 = ""

        twokriteria = 0

        if(request.form.get('kunde')):
            kunde = True
        else:
            kunde = False

        if(request.form.get('patient')):
            patient = True
        else:
            patient = False

        try:
            output = request.form['output']
        except:
            pass

        tierhaltungen = []

        if(len(kriterium1) == 0):
            pass
        elif(abfrage == "Adresse"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Adresse, Tier) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Adresse, Adresse.person_id==Person.id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .filter(Adresse.strasse.like(kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Postleitzahl"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Adresse, Tier) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Adresse, Adresse.person_id==Person.id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .filter(Adresse.postleitzahl.like(kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Kontakte"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Tier) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .filter(Person.kontakte.like("%" + kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Chipnummer"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Tier) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .filter(Tier.chip_nummer.like(kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "EU-Passnummer"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Tier) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .filter(Tier.eu_passnummer.like(kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Merkmal"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Tier) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .filter(Tier.merkmal.like(kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Rasse"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Tier) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .filter(Tier.rasse.like(kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Tierart"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Tier) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .filter(Tier.tierart.like(kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Behandlung"):
            twokriteria = 1
            von_datum, error = str_to_date(kriterium1)

            if(len(error) == 0):
                bis_datum, error = str_to_date(kriterium2)

            if(len(error) > 0):
                flash(error)
                return render_template('abfragen/index.html', abfragen=lst_abfragen, 
                            abfrage=abfrage, kriterium1=kriterium1, 
                            kriterium2=kriterium2, twokriteria=1, kunde=kunde, patient=patient, 
                            tierhaltungen=tierhaltungen, page_title="Abfragen")

            tierhaltungen = db.session.query(Tierhaltung, Person, Tier, Behandlung.tier_id) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .join(Behandlung, Behandlung.tier_id==Tier.id) \
                .filter(Behandlung.behandlungsdatum >= von_datum, Behandlung.behandlungsdatum <= bis_datum, 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Finanzamt"):
            twokriteria = 1
            von_datum, error = str_to_date(kriterium1)

            if(len(error) == 0):
                bis_datum, error = str_to_date(kriterium2)

            if(len(error) > 0):
                flash(error)
                return render_template('abfragen/index.html', abfragen=lst_abfragen, 
                            abfrage=abfrage, kriterium1=kriterium1, 
                            kriterium2=kriterium2, twokriteria=1, kunde=kunde, 
                            patient=patient, tierhaltungen=tierhaltungen, page_title="Abfragen")

            tierhaltungen = db.session.query(Tierhaltung, Person, Tier, Behandlung.tier_id) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .join(Behandlung, Behandlung.tier_id==Tier.id) \
                .filter(Behandlung.behandlungsdatum >= von_datum, Behandlung.behandlungsdatum <= bis_datum, 
                        ~Tier.merkmal.contains('Abzeichen'), #~Behandlung.diagnose.contains('Tel'),
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Impfung"):
            twokriteria = 1
            von_datum, error = str_to_date(kriterium1)

            if(len(error) == 0):
                bis_datum, error = str_to_date(kriterium2)

            if(len(error) > 0):
                flash(error)
                return render_template('abfragen/index.html', abfragen=lst_abfragen, 
                            abfrage=abfrage, kriterium1=kriterium1, 
                            kriterium2=kriterium2, twokriteria=1, kunde=kunde, 
                            patient=patient, tierhaltungen=tierhaltungen, page_title="Abfragen")

            tierhaltungen = db.session.query(Tierhaltung, Person, Tier, Behandlung.tier_id) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .join(Behandlung, Behandlung.tier_id==Tier.id) \
                .join(Impfung, Impfung.behandlung_id==Behandlung.id) \
                .filter(Behandlung.behandlungsdatum >= von_datum, Behandlung.behandlungsdatum <= bis_datum, 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Arzneien"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Tier, Behandlung) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .join(Behandlung, Behandlung.tier_id==Tier.id) \
                .filter(Behandlung.arzneien.like(kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Arzneimittel"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Tier, Behandlung) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .join(Behandlung, Behandlung.tier_id==Tier.id) \
                .filter(Behandlung.arzneimittel.like(kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        elif(abfrage == "Diagnose"):
            tierhaltungen = db.session.query(Tierhaltung, Person, Tier, Behandlung) \
                .join(Person, Person.id==Tierhaltung.person_id) \
                .join(Tier, Tier.id==Tierhaltung.tier_id) \
                .join(Behandlung, Behandlung.tier_id==Tier.id) \
                .filter(Behandlung.diagnose.like(kriterium1 + "%"), 
                        Person.kunde==kunde, Tier.patient==patient).all()
        else:
            tierhaltungen = []
    else:
        abfrage = ""
        kriterium1 = ""
        kriterium2 = ""
        twokriteria = 0
        kunde = 1
        patient = 1
        tierhaltungen = []

    if(output == "etiketten"):
        path_and_filename = dl_etiketten(abfrage, tierhaltungen)
        return send_file(path_and_filename, as_attachment=True)

    if(output == "excel"):
        path_and_filename = dl_excel(abfrage, tierhaltungen)
        return send_file(path_and_filename, as_attachment=True)

    return render_template('abfragen/index.html', abfragen=lst_abfragen, 
                            abfrage=abfrage, kriterium1=kriterium1, 
                            kriterium2=kriterium2, twokriteria=twokriteria, kunde=kunde, 
                            patient=patient, tierhaltungen=tierhaltungen, page_title="Abfragen")


@bp.route('/<int:id>/print_bericht', methods=('GET',))
@login_required
def print_bericht(id):
    print("todo...")
    return redirect(url_for('abfrage.index'))

