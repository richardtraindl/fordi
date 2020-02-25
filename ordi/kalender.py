

from datetime import date, datetime, time, timedelta

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from . import db
from ordi.auth import login_required
from ordi.models import Termin

bp = Blueprint('kalender', __name__, url_prefix='/kalender')


"""class Time:
   def wday_de:
     self.wday == 0 ? 6  : self.wday - 1
    end
end"""

AUTOREN = ["Ordi", "Elfi", "TP"]
SEK_PRO_TAG = (60 * 60 * 24)
SEK_PRO_STUNDE = (60 * 60)

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    now = datetime.now()
    aktdatum = date(now.year, now.month, now.day)
    aktzeit = time(now.hour, now.minute)
    maxkaldatum = date(2030, 12, 31)
    minkaldatum = date(2009, 1, 1)
    sek_pro_tag = SEK_PRO_TAG
    sek_pro_stunde = SEK_PRO_STUNDE

    jahre = ["2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    monate = [["Jänner", 1], ["Februar", 2], ["März", 3], ["April", 4], ["Mai", 5], ["Juni", 6], ["Juli", 7], ["August", 8], ["September", 9], ["Oktober", 10], ["November", 11], ["Dezember", 12]]
    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    
    jahr = now.year
    monat = now.month
    tag = now.day
    if(monat == 2 and tag > 29):
        tag = 29
    kaldatum = datetime(jahr, monat, tag)
    add = kaldatum.weekday() * -1
    kaldatum += timedelta(days=add)
    print(kaldatum)

    if(request.method == 'POST'):
        if(len(request.form['jahr']) > 0 and len(request.form['monat']) > 0 and
           len(request.form['tag']) > 0):
            try:
                jahr = int(request.form['jahr'])
                monat = int(request.form['monat'])
                tag = int(request.form['tag'])
                if(monat == 2 and tag > 29):
                    tag = 29
                kaldatum = datetime.date(jahr, monat, tag)
            except:
                flash("error")
                return render_template('kalender/index.html', kaldatum=kaldatum, 
                    now=now, jahre=jahre, monate=monate, page_title="Kalender")
            
            add = kaldatum.weekday() * -1
            kaldatum += datetime.timedelta(days=add)

        if(len(request.form['KWadjust']) > 0):
            try:
                adjust = int(request.form['KWadjust'])
            except:
                flash("error")
                return render_template('kalender/index.html', now=now,  
                    kaldatum=kaldatum, jahre=jahre, monate=monate,
                    page_title="Kalender")

            kaldatum += timedelta(days=adjust)

    kaldatum_ende = kaldatum + timedelta(days=6)
    termine = db.session.query(Termin) \
                .filter(Termin.beginn >= kaldatum, Termin.ende <= kaldatum_ende).all()

    return render_template('kalender/index.html', termine=termine, kaldatum=kaldatum, 
                            now=now, jahre=jahre, monate=monate, wochentage=wochentage,
                            page_title="Kalender")


@bp.route('/create', methods=('POST',))
@bp.route('/<beginn>/create', methods=('GET',))
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

        thema = request.form['thema']

        termin = Termin(autor=autor, beginn=beginn, ende=ende, thema=thema)
        db.session.add(termin)
        db.session.commit()

        return redirect(url_for('kalender.index'))
    else:
        dtbeginn = datetime.strptime(beginn, "%Y-%m-%d %H:%M:00")
        ende = dtbeginn + timedelta(hours=1)
        termin = Termin(autor="Gerold", beginn=dtbeginn, ende=ende, thema="")
    return render_template('kalender/termin.html', termin=termin, autoren=AUTOREN, page_title="Termin")


@bp.route('/<int:id>/edit', methods=('GET','POST'))
@login_required
def edit(id):
    if(request.method == 'POST'):
        termin = db.session.query(Termin).get(id)

        termin.autor = request.form['autor']

        time_begin = request.form['time_begin']
        date_begin = request.form['date_begin']
        beginn = datetime.strptime(date_begin + " " + time_begin, "%Y-%m-%d %H:%M")

        time_end = request.form['time_end']
        date_end = request.form['date_end']
        ende = datetime.strptime(date_end + " " + time_end, "%Y-%m-%d %H:%M")
         
        termin.thema = request.form['thema']

        db.session.commit()

        return redirect(url_for('kalender.index'))
    else:
        termin = db.session.query(Termin).get(id)
        return render_template('kalender/termin.html', termin=termin,  autoren=AUTOREN, page_title="Termin")


@bp.route('/<int:id>/delete', methods=('GET',))
@login_required
def delete(id):
    termin = db.session.query(Termin).get(id)
    db.session.delete(termin)
    db.session.commit()
    return redirect(url_for('kalender.index'))

