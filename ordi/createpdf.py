
import os
from flask import render_template
from fpdf import FPDF, HTMLMixin
from html.parser import HTMLParser


PDF_DIR_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdf')

def find(attrs, attribute):
    #[('id', 'fake'), 
    # ('style', 'padding-bottom: 20mm; 
    #            padding-top: 5mm;
    #            font-decoration: underline')]
    for attr in attrs:
        if(attr[0] == attribute):
            return attr[1]
        elif(attribute != "style" and attr[0] == "style"):
            styledefs = attr[1].split(";")
            print(styledefs)
            for styledef in styledefs:
                styledef = "".join(styledef.split()) #remove whitespace
                keyval = styledef.split(":")         #split into css-attribute and css-attribute-value
                if(len(keyval) == 2):
                    if(keyval[0] == attribute):
                        return keyval[1]
    return None

"""supported tags: p, div, br, hr
   supported attributes: style and within style:
      width, padding-top, padding-bottom - only in mm
      display: table, display: table-row, display: table-cell
"""
class MyHTMLParser(HTMLParser):
    def __init__(self, fpdf):
        super().__init__()
        self.fpdf = fpdf
        self.stacked_attrs = []
        self.max_y = None
        self.max_page = None
        if(self.fpdf.format == 'A4'):
            self.MAX_WIDTH = 210 - (self.fpdf.l_margin + self.fpdf.r_margin)
        else:
            self.MAX_WIDTH = 0

    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)

        self.stacked_attrs.append(attrs)

        if(tag == "br"):
            return

        if(tag == "hr"):
            self.fpdf.line(self.fpdf.x, self.fpdf.y, self.fpdf.x + 163, self.fpdf.y)
            return

        padding_top_value = find(self.stacked_attrs[-1], "padding-top")
        if(padding_top_value):
            try:
                value = int(padding_top_value.strip('mm'))
                self.fpdf.cell(w=0, h=value, border=0, txt="", ln=1, align='L')
            except:
                print("error")

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)
        padding_bottom_value = find(self.stacked_attrs[-1], "padding-bottom")
        if(padding_bottom_value):
            try:
                value = int(padding_bottom_value.strip('mm'))
                self.fpdf.cell(w=0, h=value, border=0, txt="", ln=1, align='L')
            except:
                print("error")
        self.stacked_attrs.pop()

    def handle_data(self, data):
        print("Encountered some data  :", str(len(data)) + " " + data)
        data = data.strip()
        display_value = find(self.stacked_attrs[-1], "display")
        if(display_value and display_value == "table-cell"):
            if(self.max_y == None):
                self.max_y = 0
                self.max_page = 0
            align = 'L'
            text_align_value = find(self.stacked_attrs[-1], "text-align")
            if(text_align_value):
                if(text_align_value == "center"):
                    align = 'C'
                elif(text_align_value == "right"):
                    align = 'R'

            width_value = find(self.stacked_attrs[-1], "width")                
            if(width_value):
                page = self.fpdf.page_no()
                x = self.fpdf.x
                y = self.fpdf.y
                try:
                    value = int(width_value.strip('mm'))
                    self.fpdf.multi_cell(w=value, h=5, border=0, txt=data, align=align)

                    if((self.fpdf.y > self.max_y and self.fpdf.page_no() == self.max_page) or 
                       self.fpdf.page_no() > self.max_page):
                        self.max_y = self.fpdf.y
                        self.max_page = self.fpdf.page_no()

                    if(x + value >= self.fpdf.l_margin + self.MAX_WIDTH):
                        self.fpdf.x = self.fpdf.l_margin
                        self.fpdf.y = self.max_y
                        self.fpdf.page = self.max_page
                        self.max_y = None
                        self.max_page = None
                    else:
                        self.fpdf.x = (x + value)
                        self.fpdf.y = y
                        self.fpdf.page = page
                except:
                    self.fpdf.x = x
                    self.fpdf.y = y
                    self.fpdf.page = page
                    self.max_y = None
                    self.max_page = None
                    print("error")
        else:
            if(len(data) > 0):
                self.fpdf.multi_cell(w=0, h=5, border=0, txt=data, align='L')

class HTML2PDF(FPDF, HTMLMixin):
    pass

class CustomPDF(HTML2PDF):
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


def html2pdf(html, path_and_filename):
    fpdf = CustomPDF()
    fpdf.t_margin = 25
    fpdf.r_margin = 25
    fpdf.b_margin = 25
    fpdf.l_margin = 22
    fpdf.orientation = 'P'
    fpdf.format = 'A4'
    fpdf.add_page()
    #fpdf.write_html(html)
    parser = MyHTMLParser(fpdf)
    parser.feed(html)
    fpdf.output(path_and_filename)


def html2pdf_etiketten(html, path_and_filename):
    fpdf = HTML2PDF()
    fpdf.t_margin = 20
    fpdf.r_margin = 16
    fpdf.b_margin = 26
    fpdf.l_margin = 10
    fpdf.orientation = 'P'
    fpdf.format = 'A4'
    fpdf.add_page()
    parser = MyHTMLParser(fpdf)
    parser.feed(html)
    fpdf.output(path_and_filename)

