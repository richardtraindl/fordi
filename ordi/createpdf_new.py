
import os, copy
from fpdf import FPDF
from ordi.util.filters import *


class CustomPDF(FPDF):
    def header(self):
        self.image(name=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img', 'logo.png'), 
                   x=160, y=25, w=25, h=25) 

        self.set_font('Arial', '', 11)
        self.cell(85)
        self.cell(w=50, h=4, txt='', ln=1)

        self.set_font('Arial', '', 11)
        self.cell(85)
        text1 = 'TIERARZTPRAXIS'
        self.cell(w=50, h=4, txt=text1, ln=1, align='C')
        
        self.set_font('Arial', 'U', 11)
        self.cell(85)
        text2 = 'Kaiserstrasse'
        self.cell(w=50, h=4, txt=text2, ln=1, align='C')

        self.set_font('Arial', '', 11)
        self.cell(85)
        self.cell(w=50, h=2, txt='', ln=1)

        self.set_font('Arial', '', 11)
        self.cell(85)
        text3 = 'Dr. Elfriede Koppensteiner'
        self.cell(w=50, h=4, txt=text3, ln=1, align='R')

        self.cell(85)
        text4 = 'Mag. Gerold Koppensteiner'
        self.cell(w=50, h=4, txt=text4, ln=1, align='R')

        self.ln(20)
 
 
    def footer(self):
        self.set_y(-17)

        self.set_font('Arial', '', 10)

        bankverbindung = 'Bankverbindung HYPO NOE Landesbank AG, IBAN: AT96 5300 0016 5501 9002'
        self.cell(w=0, h=5, txt=bankverbindung, ln=1, align='L')

        kontakt = '1070 Tierarztpraxis Kaiserstrasse, Tel. 01 944 5 944, 0699 1 944 5 944 ATU 56934599'
        self.cell(w=0, h=5, txt=kontakt, align='L')


def write_rechnung_table(fpdf, rechnungszeilen, width, height, spacing):
    for rzeile in rechnungszeilen:
        fpdf.cell(width * 0.2, height*spacing, txt=filter_format_date(rzeile.datum), border=0)
        fpdf.cell(width * 0.6, height*spacing, txt=rzeile.artikel, border=0)
        fpdf.cell(width * 0.2, height*spacing, txt='{0:0.2f}'.format(float(rzeile.betrag)), border=0, align='R')
        fpdf.ln(height*spacing)

def create_rechnung_pdf(rechnung, rechnungszeilen):
    fpdf = CustomPDF()
    fpdf.t_margin = 25
    fpdf.r_margin = 25
    fpdf.b_margin = 25
    fpdf.l_margin = 22
    fpdf.orientation = 'P'
    fpdf.format = 'A4'
    fpdf.add_page()

    spacing = 1.2
    width = 163 #210 - (25 + 22) = 163
    height = fpdf.font_size

    anrede = mapanrede(rechnung.person.anredecode)
    fpdf.cell(width, height*spacing, txt=anrede, border=0)
    fpdf.ln(height*spacing)

    name = rechnung.person.vorname + " " + rechnung.person.familienname + " " + rechnung.person.titel
    fpdf.cell(width, height*spacing, txt=name, border=0)
    fpdf.ln(height*spacing)

    fpdf.cell(width, height*spacing, txt=rechnung.person.adr_strasse, border=0)
    fpdf.ln(height*spacing)

    plz_ort = rechnung.person.adr_plz + " " + rechnung.person.adr_ort
    fpdf.cell(width, height*spacing, txt=plz_ort, border=0)
    fpdf.ln(20)

    fpdf.set_font('Arial', 'B', 11)
    jahr_lfnr = "Rechnung: " + str(rechnung.jahr) + "/" + str(rechnung.lfnr)
    fpdf.cell(width, height*spacing, txt=jahr_lfnr, border=0)
    fpdf.ln(10)

    fpdf.set_font('Arial', '', 11)
    col1_width = width * 0.7
    col2_width = width * 0.3
    height = fpdf.font_size

    patient = "Patient: " + rechnung.tier.tiername  + " " + rechnung.tier.tierart
    if(rechnung.tier.geburtsdatum):
        patient += ", geb. " + filter_format_date(rechnung.tier.geburtsdatum)
    fpdf.cell(col1_width, height*spacing, txt=patient, border=0)
    date = filter_format_date(rechnung.datum)
    fpdf.cell(col2_width, height*spacing, txt=date, align='R', border=0)
    fpdf.ln(5)

    chip = "Chip: " + rechnung.tier.chip_nummer
    fpdf.cell(width, height*spacing, txt=chip, border=0)
    fpdf.ln(5)

    diagnose = "Diagnose: " + rechnung.diagnose
    fpdf.multi_cell(width, height*spacing, txt=diagnose, border=0)
    fpdf.ln(10)

    rechnunglegung = "Für tierärztliche Leistung und Medikamente erlaube ich mir zu berechnen."
    fpdf.cell(width, height*spacing, txt=rechnunglegung, border=0)
    fpdf.ln(10)

    write_rechnung_table(fpdf, rechnungszeilen, width, height, spacing)

    fpdf.line(fpdf.x, fpdf.y, fpdf.x + 163, fpdf.y)
    fpdf.ln(1)

    fpdf.cell(width * 0.7, height*spacing, txt="Summe netto EUR", border=0)
    fpdf.cell(width * 0.3, height*spacing, txt='{0:0.2f}'.format(float(rechnung.netto_summe)), border=0, align='R')
    fpdf.ln(5)

    fpdf.cell(width * 0.7, height*spacing, txt="10% Umsatzsteuer", border=0)
    fpdf.cell(width * 0.3, height*spacing, txt='{0:0.2f}'.format(float(rechnung.steuerbetrag_zehn)), border=0, align='R')
    fpdf.ln(5)

    fpdf.cell(width * 0.7, height*spacing, txt="13% Umsatzsteuer", border=0)
    fpdf.cell(width * 0.3, height*spacing, txt='{0:0.2f}'.format(float(rechnung.steuerbetrag_dreizehn)), border=0, align='R')
    fpdf.ln(5)

    fpdf.cell(width * 0.7, height*spacing, txt="20% Umsatzsteuer", border=0)
    fpdf.cell(width * 0.3, height*spacing, txt='{0:0.2f}'.format(float(rechnung.steuerbetrag_zwanzig)), border=0, align='R')
    fpdf.ln(5)

    fpdf.line(fpdf.x, fpdf.y, (fpdf.x + 163), fpdf.y)
    fpdf.ln(1)

    fpdf.set_font('Arial', 'B', 11)
    fpdf.cell(width * 0.7, height*spacing, txt="Endsumme Brutto EUR", border=0)
    fpdf.cell(width * 0.3, height*spacing, txt='{0:0.2f}'.format(float(rechnung.brutto_summe)), border=0, align='R')
    fpdf.ln(10)

    fpdf.set_font('Arial', '', 11)
    bezahlung = "Zahlung: " + rechnung.bezahlung
    fpdf.cell(width, height*spacing, txt=bezahlung, border=0)
    fpdf.ln(height*spacing)

    byte_string = fpdf.output(dest="S").encode('latin-1')
    return byte_string


def create_behandlungsverlauf_pdf(behandlungsverlauf):
    fpdf = CustomPDF()
    fpdf.t_margin = 25
    fpdf.r_margin = 25
    fpdf.b_margin = 25
    fpdf.l_margin = 22
    fpdf.orientation = 'P'
    fpdf.format = 'A4'
    fpdf.add_page()

    spacing = 1.2
    width = 163 #210 - (25 + 22) = 163
    height = fpdf.font_size

    anrede = mapanrede(behandlungsverlauf.person.anredecode)
    fpdf.cell(width, height*spacing, txt=anrede, border=0)
    fpdf.ln(height*spacing)

    name = behandlungsverlauf.person.vorname + " " + behandlungsverlauf.person.familienname + " " + behandlungsverlauf.person.titel
    fpdf.cell(width, height*spacing, txt=name, border=0)
    fpdf.ln(height*spacing)

    fpdf.cell(width, height*spacing, txt=behandlungsverlauf.person.adr_strasse, border=0)
    fpdf.ln(height*spacing)

    plz_ort = behandlungsverlauf.person.adr_plz + " " + behandlungsverlauf.person.adr_ort
    fpdf.cell(width, height*spacing, txt=plz_ort, border=0)
    fpdf.ln(20)

    patient = "Patient: " + behandlungsverlauf.tier.tiername  + " " + behandlungsverlauf.tier.tierart
    if(behandlungsverlauf.tier.geburtsdatum):
        patient += ", geb. " + filter_format_date(behandlungsverlauf.tier.geburtsdatum)
    col1_width = width * 0.7
    col2_width = width * 0.3
    fpdf.cell(col1_width, height*spacing, txt=patient, border=0)
    datum = filter_format_date(behandlungsverlauf.datum)
    fpdf.cell(col2_width, height*spacing, txt=datum, align='R', border=0)
    fpdf.ln(10)

    diagnose = "Diagnose: " + behandlungsverlauf.diagnose
    fpdf.cell(width, height*spacing, txt=diagnose, border=0)
    fpdf.ln(20)

    fpdf.multi_cell(width, height*spacing, txt=behandlungsverlauf.behandlung, border=0)
    fpdf.ln(height*spacing)

    byte_string = fpdf.output(dest="S").encode('latin-1')
    return byte_string


def write_abfrage_table(fpdf, tierhaltungen, width, height, spacing):
    fpdf.set_font('Arial', 'B', 11)
    fpdf.cell(width * 0.4, height*spacing, txt="Familienname", border=0)
    fpdf.cell(width * 0.6, height*spacing, txt="Tiername", border=0)
    fpdf.ln(height*spacing)

    fpdf.set_font('Arial', '', 11)
    for tierhaltung in tierhaltungen:
        fpdf.cell(width * 0.4, height*spacing, txt=tierhaltung.Person.familienname, border=0)
        fpdf.cell(width * 0.6, height*spacing, txt=tierhaltung.Tier.tiername, border=0)
        fpdf.ln(height*spacing)

def create_abfrage_pdf(abfrage, kriterium1, kriterium2, tierhaltungen):
    fpdf = FPDF()
    fpdf.t_margin = 20
    fpdf.r_margin = 16
    fpdf.b_margin = 26
    fpdf.l_margin = 10
    fpdf.orientation = 'P'
    fpdf.format = 'A4'
    fpdf.set_font('Arial', '', 11)
    fpdf.add_page()

    spacing = 1.2
    width = 184 #210 - (16 + 10) = 184
    height = fpdf.font_size

    fpdf.set_font('Arial', '', 18)
    topic_height = fpdf.font_size
    abfrage = "Abfrage " + abfrage + " " + kriterium1 + " " + kriterium2
    fpdf.cell(width, topic_height*spacing, txt=abfrage, border=0)
    fpdf.ln(10)

    fpdf.set_font('Arial', '', 11)
    write_abfrage_table(fpdf, tierhaltungen, width, height, spacing)

    byte_string = fpdf.output(dest="S").encode('latin-1')
    return byte_string


def write_etiketten_table(fpdf, personen, width, height, spacing):
    col_width = width // 3
    startx = fpdf.x
    for index, person in enumerate(personen):
        parenty = fpdf.y

        anrede = mapanrede(person.anredecode) + " " + person.titel
        fpdf.cell(col_width, height*spacing, txt=anrede, border=0)
        fpdf.ln(height*spacing)
        fpdf.x = startx + (col_width * (index % 3))

        name = person.familienname + " " + person.vorname
        fpdf.cell(col_width, height*spacing, txt=name, border=0)
        fpdf.ln(height*spacing)
        fpdf.x = startx + (col_width * (index % 3))

        fpdf.cell(col_width, height*spacing, txt=person.adr_strasse, border=0)
        fpdf.ln(height*spacing)
        fpdf.x = startx + (col_width * (index % 3))

        plz_ort = person.adr_plz + " " + person.adr_ort
        fpdf.cell(col_width, height*spacing, txt=plz_ort, border=0)

        if(index % 3 != 2):
            fpdf.y = parenty
        if(index % 3 == 2):
            fpdf.ln(10)

def create_etiketten_pdf(personen):
    fpdf = FPDF()
    fpdf.t_margin = 20
    fpdf.r_margin = 16
    fpdf.b_margin = 26
    fpdf.l_margin = 10
    fpdf.orientation = 'P'
    fpdf.format = 'A4'
    fpdf.set_font('Arial', '', 11)
    fpdf.add_page()

    spacing = 1.2
    width = 184 #210 - (16 + 10) = 184
    height = fpdf.font_size

    write_etiketten_table(fpdf, personen, width, height, spacing)

    byte_string = fpdf.output(dest="S").encode('latin-1')
    return byte_string
