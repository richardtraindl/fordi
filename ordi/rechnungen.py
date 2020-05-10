

from datetime import datetime
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

bp = Blueprint('rechnung', __name__, url_prefix='/rechnung')


@bp.route('/index', methods=('GET', 'POST'))
@login_required
def index():
    if(request.method == 'POST'):
        try:
            rechnungsjahr = int(request.form['rechnungsjahr'])
        except:
            rechnungsjahr = None
    else:
        rechnungsjahr = None

    if(rechnungsjahr):
        rechnungen = db.session.query(Rechnung, Person, Tier) \
            .join(Person, Rechnung.person_id == Person.id) \
            .join(Tier, Rechnung.tier_id == Tier.id).filter(Rechnung.rechnungsjahr==rechnungsjahr).all()
    else:
        rechnungen = db.session.query(Rechnung, Person, Tier) \
            .join(Person, Rechnung.person_id == Person.id) \
            .join(Tier, Rechnung.tier_id == Tier.id).all()
        
    if(rechnungsjahr):
        str_rechnungsjahr = str(rechnungsjahr)
    else:
        str_rechnungsjahr = ""
    return render_template('rechnungen/index.html', rechnungen=rechnungen, rechnungsjahr=str_rechnungsjahr, page_title="Rechnungen")


def calc_and_fill_rechnung(rechnung, rechnungszeilen):
    rechnung.brutto_summe = 0
    rechnung.steuerbetrag_zwanzig = 0
    rechnung.steuerbetrag_dreizehn = 0
    rechnung.steuerbetrag_zehn = 0

    for rechnungszeile in rechnungszeilen:
        try:
            steuersatz = ARTIKEL_STEUER[rechnungszeile.artikelcode]
        except:
            return "Falsche Artikelart."
        try:
            betrag = round(rechnungszeile.betrag, 2)
        except:
            return "Betrag ist keine Zahl."

        rechnung.brutto_summe += betrag
        nettobetrag = round(betrag * 100 / (100 + steuersatz))
        if(steuersatz == 20):
            rechnung.steuerbetrag_zwanzig += (betrag - nettobetrag)
        elif(steuersatz == 13):
            rechnung.steuerbetrag_dreizehn += (betrag - nettobetrag)
        else: # steuersatz == 10
            rechnung.steuerbetrag_zehn += (betrag - nettobetrag)

    rechnung.netto_summe = rechnung.brutto_summe - (rechnung.steuerbetrag_zwanzig + rechnung.steuerbetrag_dreizehn + rechnung.steuerbetrag_zehn)
    return ""

def dl_rechnung(rechnung_id):
    rechnung = db.session.query(Rechnung).get(rechnung_id)
    rechnungszeilen = db.session.query(Rechnungszeile).filter(Rechnungszeile.rechnung_id==rechnung_id).all()

    html = render_template('rechnungen/print_rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen)

    filename = str(rechnung.id) + "_rechnung_fuer_" + rechnung.person.familienname + "_" + rechnung.person.vorname + ".pdf"
    path_and_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', filename)

    html2pdf(html, path_and_filename)

    return path_and_filename

@bp.route('/<int:id>/create', methods=('GET', 'POST'))
@login_required
def create(id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])

    tierhaltung = db.session.query(Tierhaltung).get(id)

    if(request.method == 'POST'):
        rechnung, error = fill_and_validate_rechnung(None, request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        if(len(req_rechnungszeilen) == 0):
            error += "Es muss mind. eine Rechnungszeile vorhanden sein. "
        if(len(error) > 0):
            flash(error)
            return render_template('rechnungen/rechnung.html', id=id, rechnung=rechnung, 
                rechnungszeilen=req_rechnungszeilen, person = tierhaltung.person, 
                tier = tierhaltung.tier, artikelwerte=artikelwerte, page_title="Rechnung")

        rechnungszeilen = []
        for req_rechnungszeile in req_rechnungszeilen:
            rechnungszeile, error = fill_and_validate_rechnungszeile(None, req_rechnungszeile)
            if(len(error) > 0):
                flash(error)
                return render_template('rechnungen/rechnung.html', id=id, rechnung=rechnung, 
                    rechnungszeilen=req_rechnungszeilen, person = tierhaltung.person, 
                    tier = tierhaltung.tier, artikelwerte=artikelwerte, page_title="Rechnung")
            else:
                rechnungszeilen.append(rechnungszeile)

        error = calc_and_fill_rechnung(rechnung, rechnungszeilen)
        if(len(error) > 0):
            flash(error)
            return render_template('rechnungen/rechnung.html', id=id, rechnung=rechnung, 
                rechnungszeilen=req_rechnungszeilen, person = tierhaltung.person, 
                tier = tierhaltung.tier, artikelwerte=artikelwerte, page_title="Rechnung")

        rechnung.person_id = tierhaltung.person.id
        rechnung.tier_id = tierhaltung.tier.id
        db.session.add(rechnung)
        db.session.commit()

        for rechnungszeile in rechnungszeilen:
            rechnungszeile.rechnung_id = rechnung.id
            db.session.add(rechnungszeile)
        db.session.commit()
        return redirect(url_for('rechnung.edit', rechnung_id=rechnung.id))
    else:
        datum = datetime.now().strftime("%Y-%m-%d")
        ort = "Wien"
        return render_template('rechnungen/rechnung.html', id=id, rechnung=None, 
            rechnungszeilen=None, person = tierhaltung.person, tier = tierhaltung.tier, 
            datum=datum, ort=ort, artikelwerte=artikelwerte, page_title="Rechnung")


@bp.route('/<int:rechnung_id>/edit', methods=('GET', 'POST'))
@login_required
def edit(rechnung_id):
    artikelwerte = []
    for key, value in ARTIKEL.items():
        artikelwerte.append([key, value])

    rechnung = db.session.query(Rechnung).get(rechnung_id)
    rechnungszeilen = db.session.query(Rechnungszeile).filter(Rechnungszeile.rechnung_id==rechnung.id).all()

    if(request.method == 'POST'):
        rechnung, error = fill_and_validate_rechnung(rechnung, request)
        req_rechnungszeilen = build_rechnungszeilen(request)
        if(len(req_rechnungszeilen) == 0):
            error += "Es muss mind. eine Rechnungszeile vorhanden sein. "
        if(len(error) > 0):
            flash(error)
            return render_template('rechnungen/rechnung.html', rechnung=rechnung, rechnungszeilen=req_rechnungszeilen, 
                artikelwerte=artikelwerte, page_title="Rechnung")

        new_rechnungszeilen = []
        for req_rechnungszeile in req_rechnungszeilen:
            new_rechnungszeile = None
            if(len(req_rechnungszeile['rechnungszeile_id']) > 0):
                try:
                    rechnungszeile_id = int(req_rechnungszeile['rechnungszeile_id'])
                    new_rechnungszeile = db.session.query(Rechnungszeile).get(rechnungszeile_id)
                except:
                    rechnungszeile_id = None

            new_rechnungszeile, error = fill_and_validate_rechnungszeile(new_rechnungszeile, req_rechnungszeile)
            if(len(error) > 0):
                flash(error)
                return render_template('rechnungen/rechnung.html', rechnung=rechnung, rechnungszeilen=req_rechnungszeilen, 
                    artikelwerte=artikelwerte, page_title="Rechnung")
            else:
                new_rechnungszeilen.append(new_rechnungszeile)

        error = calc_and_fill_rechnung(rechnung, new_rechnungszeilen)
        if(len(error) > 0):
            flash(error)
            return render_template('rechnungen/rechnung.html', rechnung=rechnung, rechnungszeilen=req_rechnungszeilen, 
                artikelwerte=artikelwerte, page_title="Rechnung")

        db.session.commit() # commit rechnung

        for new_rechnungszeile in new_rechnungszeilen:
            if(new_rechnungszeile.id == None):
                new_rechnungszeile.rechnung_id = rechnung.id
                db.session.add(new_rechnungszeile)
        db.session.commit()

        for rechnungszeile in rechnungszeilen:
            found = False
            for new_rechnungszeile in new_rechnungszeilen:
                if(rechnungszeile.id == new_rechnungszeile.id):
                    found = True
                    break
            if(found == False):
                db.session.delete(rechnungszeile)
        db.session.commit()

        path_and_filename = dl_rechnung(rechnung.id)
        return send_file(path_and_filename, as_attachment=True)
    else:
        return render_template('rechnungen/rechnung.html', rechnung=rechnung, rechnungszeilen=rechnungszeilen, artikelwerte=artikelwerte, 
            page_title="Rechnung")


@bp.route('/<int:rechnung_id>/delete', methods=('GET',))
@login_required
def delete(rechnung_id):
    rechnung = db.session.query(Rechnung).get(rechnung_id)
    db.session.delete(rechnung)
    db.session.commit()
    return redirect(url_for('rechnung.index'))


@bp.route('/<int:rechnungszeile_id>/delete_rechnungszeile', methods=('GET',))
@login_required
def delete_rechnungszeile(rechnungszeile_id):
    rechnungszeile = db.session.query(Rechnungszeile).get(rechnungszeile_id)
    db.session.delete(rechnungszeile)
    db.session.commit()
    return redirect(url_for('rechnung.edit', rechnung_id=rechnungszeile.rechnung_id))

