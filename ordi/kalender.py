

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
        if(len(request.form['Jahr']) > 0 and len(request.form['Monat']) > 0 and
           len(request.form['Tag']) > 0):
            try:
                jahr = int(request.form['Jahr'])
                monat = int(request.form['Monat'])
                tag = int(request.form['Tag'])
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


@bp.route('/<beginn>/create', methods=('GET','POST'))
@login_required
def create(beginn):
    if(request.method == 'POST'):

    else:
        str_beginn = request.form['beginn']
        beginn = datetime.strptime(str_beginn, "%Y-%m-%d %H:%M:00")
	ende = 
        beginn = datetime.now()
"""  def new
		@termin				 = Termin.new
		@termin.beginn = Time.at(Integer(params[:beginn]))
		@termin.ende   = @termin.beginn + 15.minutes
  end


  def build_datetime_from_params( params, field_name )
    DateTime.new(      
      params["#{field_name.to_s}(1i)"].to_i,
      params["#{field_name.to_s}(2i)"].to_i,
      params["#{field_name.to_s}(3i)"].to_i,
      params["#{field_name.to_s}(4i)"].to_i,
      params["#{field_name.to_s}(5i)"].to_i
      )      
  end


  def create
		@termin 			 = Termin.new
	  @termin.autor  = params[:termin][:autor]
	  @termin.thema  = params[:termin][:thema]
		@termin.beginn = Time.gm(
												(params[:termin][:date_begin].to_s[6,4]).to_i,
												(params[:termin][:date_begin].to_s[3,2]).to_i,
												(params[:termin][:date_begin].to_s[0,2]).to_i, 
												(params[:termin][:time_begin].to_s[0,2]).to_i, 
												(params[:termin][:time_begin].to_s[3,2]).to_i,
												0, 0)
		@termin.ende = Time.gm(
												(params[:termin][:date_end].to_s[6,4]).to_i,
												(params[:termin][:date_end].to_s[3,2]).to_i,
												(params[:termin][:date_end].to_s[0,2]).to_i,
												(params[:termin][:time_end].to_s[0,2]).to_i,
												(params[:termin][:time_end].to_s[3,2]).to_i,
												0, 0)
	  
	  # @termin.beginn = build_datetime_from_params( params[:termin], "beginn" )
		# @termin.ende   = build_datetime_from_params( params[:termin], "ende" )

		if( @termin.beginn > @termin.ende )
		    flash[:error] = 'Ende liegt vor Beginn.'
      	render :action => "new", :beginn => @termin.beginn, :ende => @termin.ende
		elsif( @termin.thema.length == 0 )
		    flash[:error] = 'Eingabe für Thema fehlt.'
      	render :action => "new", :beginn => @termin.beginn, :ende => @termin.ende		
		else
	    if @termin.save
	        flash[:notice] = 'Termin erfolgreich gespeichert.'
	        redirect_to :action => "index", :Jahr => @termin.beginn.year, :Monat => @termin.beginn.month, :Tag => @termin.beginn.day
	    else
	        flash[:notice] = 'Fehler beim Speichern des Termins.'
	        render :action => "new"
	    end
	   end
  end


  def edit
  	@kaldatum = Time.gm(params[:kjahr].to_i, params[:kmonat].to_i, params[:ktag].to_i)
		@termin	= Termin.find(params[:id])
  end


  def update
    @termin = Termin.find(params[:id])
    @termin.autor = params[:termin][:autor]
    @termin.thema = params[:termin][:thema]
    # @termin.beginn = build_datetime_from_params( params[:termin], "beginn" )
		# @termin.ende   = build_datetime_from_params( params[:termin], "ende" )
		@termin.beginn = Time.gm(
												(params[:termin][:date_begin].to_s[6,4]).to_i,
												(params[:termin][:date_begin].to_s[3,2]).to_i,
												(params[:termin][:date_begin].to_s[0,2]).to_i, 
												(params[:termin][:time_begin].to_s[0,2]).to_i, 
												(params[:termin][:time_begin].to_s[3,2]).to_i,
												0, 0)
		@termin.ende = Time.gm(
												(params[:termin][:date_end].to_s[6,4]).to_i,
												(params[:termin][:date_end].to_s[3,2]).to_i,
												(params[:termin][:date_end].to_s[0,2]).to_i,
												(params[:termin][:time_end].to_s[0,2]).to_i,
												(params[:termin][:time_end].to_s[3,2]).to_i,
												0, 0)

		if( @termin.beginn > @termin.ende )
		    flash[:error] = 'Ende liegt Beginn.'
      	render :action => "edit", :id => @termin.id
		elsif( @termin.thema.length == 0 )
		    flash[:error] = 'Eingabe für Thema fehlt.'
      	render :action => "edit", :id => @termin.id
		else
		  	if @termin.update_attributes(:autor => @termin.autor, :thema => @termin.thema, :beginn => @termin.beginn, :ende => @termin.ende )
		        flash[:notice] = 'Termin erfolgreich geändert.'
		        redirect_to :action => "index", :Jahr => @termin.beginn.year, :Monat => @termin.beginn.month, :Tag => @termin.beginn.day
		    else
		      	flash[:notice] = 'Fehler beim Speichern des Termins.'
		        render :action => "edit"
		    end
	  end
  end


  def destroy
		@termin = Termin.find(params[:id])
		jahr = @termin.beginn.year
		monat = @termin.beginn.month
		tag = @termin.beginn.day

		if @termin.destroy
			flash[:notice] = 'Termin erfolgreich gelöscht.'
		else
			flash[:notice] = 'Fehler beim Löschen des Termins.'
		end
		redirect_to :action => "index", :Jahr => jahr, :Monat => monat, :Tag => tag
  end


end """
