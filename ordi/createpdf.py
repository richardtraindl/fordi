
import os
from flask import render_template
from fpdf import FPDF, HTMLMixin
from html.parser import HTMLParser


PDF_DIR_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdf')

def split_attrs(attrs):
    props = []
    for attr in attrs:
        if(len(attr) > 1 and attr[0] == "style"):
            items = attr[1].split(";")
            for item in items:
                item = "".join(item.split())
                props.append(item.split(":"))
    return props

class MyHTMLParser(HTMLParser):
    def __init__(self, pdf):
        super().__init__()
        self.pdf = pdf
        self.prop_for_endtag = []

    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)
        if(tag == "div"):
            props = split_attrs(attrs)
            for prop in props:
                if(prop[0] == "padding-bottom"):
                    self.prop_for_endtag = prop
                    continue
                elif(prop[0] == "padding-top"):
                    try:
                        val = int(prop[1].strip('mm'))
                    except:
                        print("error")
                        continue
                    self.pdf.cell(w=0, h=val, border=1, txt=" sss*** ", ln=1, align='L')

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)
        if(tag == "div"):
            if(len(self.prop_for_endtag) > 0):
                print("fff" + self.prop_for_endtag[0])
                if(self.prop_for_endtag[0] == "padding-bottom"):
                    try:
                        print("fff" + self.prop_for_endtag[1])
                        val = int(self.prop_for_endtag[1].strip('mm'))
                        self.pdf.cell(w=0, h=val, border=1, txt=" eee*** ", ln=1, align='L')
                    except:
                        print("error")
                    self.prop_for_endtag.clear()

    def handle_data(self, data):
        print("Encountered some data  :", str(len(data)) + " " + data)
        testdata = "".join(data.split())
        if(len(testdata) > 0):
            self.pdf.cell(w=0, h=5, border=1, txt=data + " *** ", ln=1, align='L')


class HTML2PDF(FPDF, HTMLMixin):
    pass

class CustomPDF(HTML2PDF):
    def header(self):
        # Set up a logo
        self.image(name=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img', 'logo.png'), 
                   x=160, y=25, w=25, h=25) 

        self.set_font('Arial', '', 11)
        self.cell(85)
        self.cell(w=50, h=4, txt='', ln=1)

        # Add an address
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

         # Line break
        self.ln(20)
 
    def footer(self):
        self.set_y(-27)

        self.set_font('Arial', '', 10)

        bankverbindung = 'Bankverbindung HYPO NOE Landesbank AG, IBAN: AT96 5300 0016 5501 9002'
        self.cell(w=0, h=5, txt=bankverbindung, ln=1, align='L')

        kontakt = '1070 Tierarztpraxis Kaiserstrasse, Tel. 01 944 5 944, 0699 1 944 5 944 ATU 56934599'
        self.cell(w=0, h=5, txt=kontakt, align='L')


def html2pdf(html, path_and_filename):
    pdf = CustomPDF()
    pdf.l_margin = 22
    pdf.r_margin = 25
    pdf.t_margin = 25
    pdf.b_margin = 17
    pdf.add_page()
    #pdf.write_html(html)
    parser = MyHTMLParser(pdf)
    parser.feed(html) #'<html><head><title>Test</title></head><body><h1>Parse me!</h1><div class="row"><div class="cell">c1</div><div class="cell">c2</div><div class="cell">c3</div></div></body></html>')
    pdf.output(path_and_filename)

