

from datetime import date, datetime, time, timedelta

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from . import db
from sqlalchemy import or_, and_
from ordi.auth import login_required
from ordi.models import Termin

bp = Blueprint('kalender', __name__, url_prefix='/kalender')


AUTOREN = ["Ordi", "Elfi", "TP"]
jahre = [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
monate = [["Jänner", 1], ["Februar", 2], ["März", 3], ["April", 4], ["Mai", 5], ["Juni", 6], ["Juli", 7], ["August", 8], ["September", 9], ["Oktober", 10], ["November", 11], ["Dezember", 12]]
wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

def calc_kaldatum(datum):
    aktdatum = datetime(year=datum.year, month=datum.month, day=datum.day)
    add = aktdatum.weekday() * -1
    return aktdatum + timedelta(days=add)

@bp.route('/', methods=('GET', 'POST'))
@bp.route('/index', methods=('GET', 'POST'))
@bp.route('/<kaldatum>/index', methods=('GET', 'POST'))
@login_required
def index(kaldatum=None):
    now = datetime.now()
    hour = (now.hour // 15)  * 15
    aktdatum = datetime(year=now.year, month=now.month, day=now.day, hour=hour)

    if(kaldatum):
        datum = datetime.strptime(kaldatum, "%Y-%m-%d %H:%M:00")
        kaldatum = calc_kaldatum(datum)
    else:
        kaldatum = calc_kaldatum(aktdatum)

    if(request.method == 'POST'):
        if(len(request.form['kjahr']) > 0 and len(request.form['kmonat']) > 0 and
           len(request.form['ktag']) > 0):
            try:
                kjahr = int(request.form['kjahr'])
                kmonat = int(request.form['kmonat'])
                ktag = int(request.form['ktag'])
                datum = datetime(year=kjahr, month=kmonat, day=ktag)
                kaldatum = calc_kaldatum(datum)
            except:
                flash("error")
                return render_template('kalender/index.html', aktdatum=aktdatum, 
                                        kaldatum=kaldatum, jahre=jahre, monate=monate, 
                                        wochentage=wochentage, page_title="Kalender")

        if(len(request.form['kwadjust']) > 0):
            try:
                adjust = int(request.form['kwadjust'])
            except:
                flash("error")
                return render_template('kalender/index.html', aktdatum=aktdatum, 
                                        kaldatum=kaldatum, jahre=jahre, monate=monate, 
                                        wochentage=wochentage, page_title="Kalender")

            kaldatum += timedelta(weeks=adjust)

    kaldatum_ende = kaldatum + timedelta(days=7)

    termine = db.session.query(Termin) \
                .filter(or_(and_(Termin.beginn < kaldatum, Termin.ende > kaldatum), 
                            and_(Termin.beginn >= kaldatum, Termin.beginn < kaldatum_ende))).all()

    return render_template('kalender/index.html', termine=termine, aktdatum=aktdatum, 
                            kaldatum=kaldatum, jahre=jahre, monate=monate, 
                            wochentage=wochentage, page_title="Kalender")


@bp.route('/create', methods=('GET', 'POST'))
@bp.route('/<beginn>/create', methods=('GET', 'POST'))
@login_required
def create(beginn=None):
    if(request.method == 'POST'):
        autor = request.form['autor']

        time_begin = request.form['time_begin']
        date_begin = request.form['date_begin']
        beginn = datetime.strptime(date_begin + " " + time_begin, "%Y-%m-%d %H:%M")

        time_end = request.form['time_end']
        date_end = request.form['date_end']
        ende = datetime.strptime(date_end + " " + time_end, "%Y-%m-%d %H:%M")

        if(beginn >= ende):
            flash("Beginn liegt nach Ende!")
            return render_template('kalender/termin.html', termin=None, 
                                   autoren=AUTOREN, page_title="Termin")

        thema = request.form['thema']

        termin = Termin(autor=autor, beginn=beginn, ende=ende, thema=thema)
        db.session.add(termin)
        db.session.commit()

        return redirect(url_for('kalender.index', 
                                kaldatum=termin.beginn))
    else:
        if(beginn):
            dtbeginn = datetime.strptime(beginn, "%Y-%m-%d %H:%M:00")
        else:
            datum = datetime.now()
            hour = (datum.hour // 15)  * 15
            dtbeginn = datetime(year=datum.year, month=datum.month, day=datum.day, hour=hour)
        ende = dtbeginn + timedelta(hours=1)
        termin = Termin(autor="Gerold", beginn=dtbeginn, ende=ende, thema="")
        return render_template('kalender/termin.html', termin=termin, 
                               autoren=AUTOREN, page_title="Termin")


@bp.route('/<int:id>/edit', methods=('GET','POST'))
@login_required
def edit(id):
    termin = db.session.query(Termin).get(id)

    if(request.method == 'POST'):
        termin.autor = request.form['autor']

        time_begin = request.form['time_begin']
        date_begin = request.form['date_begin']
        termin.beginn = datetime.strptime(date_begin + " " + time_begin, "%Y-%m-%d %H:%M")

        time_end = request.form['time_end']
        date_end = request.form['date_end']
        termin.ende = datetime.strptime(date_end + " " + time_end, "%Y-%m-%d %H:%M")

        if(termin.beginn >= termin.ende):
            flash("Beginn liegt nach Ende!")
            return render_template('kalender/termin.html', termin=termin, 
                                    autoren=AUTOREN, page_title="Termin")

        termin.thema = request.form['thema']

        db.session.commit()

        return redirect(url_for('kalender.index', kaldatum=termin.beginn))
    else:
        return render_template('kalender/termin.html', termin=termin,  
                               autoren=AUTOREN, page_title="Termin")


@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id):
    termin = db.session.query(Termin).get(id)
    db.session.delete(termin)
    db.session.commit()
    return redirect(url_for('kalender.index'))

