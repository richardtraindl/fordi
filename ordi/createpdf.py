
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

class MyHTMLParser(HTMLParser):
    MAX_WIDTH = 163
    def __init__(self, pdf):
        super().__init__()
        self.pdf = pdf
        self.cur_tag = None
        self.cur_attrs = []
        self.curr_row_width = 0

    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)
        print(attrs)
        self.cur_tag = tag
        self.cur_attrs = attrs

        padding_top_value = find(attrs, "padding-top")
        if(padding_top_value):
            try:
                value = int(padding_top_value.strip('mm'))
                self.pdf.cell(w=0, h=value, border=1, txt="top*** ", ln=1, align='L')
            except:
                print("error")

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)
        print(self.cur_attrs)
        padding_bottom_value = find(self.cur_attrs, "padding-bottom")
        print("VVVVVVVVVVVVVVVVVVVVVv")
        print(self.cur_attrs)
        print(padding_bottom_value)
        if(padding_bottom_value):
            try:
                value = int(padding_bottom_value.strip('mm'))
                self.pdf.cell(w=0, h=value, border=1, txt="bot*** ", ln=1, align='L')
            except:
                print("error")

    def handle_data(self, data):
        print("Encountered some data  :", str(len(data)) + " " + data)
        data = data.strip()
        if(len(data) > 0):
            display_value = find(self.cur_attrs, "display")
            if(display_value and display_value == "table-cell"):
                align = 'L'
                text_align_value = find(self.cur_attrs, "text-align")
                if(text_align_value):
                    if(text_align_value == "center"):
                        align = 'C'
                    elif(text_align_value == "right"):
                        align = 'R'

                width_value = find(self.cur_attrs, "width")                
                if(width_value):
                    try:
                        value = int(width_value.strip('mm'))
                        self.curr_row_width += value
                        print(str(self.curr_row_width))
                        if(self.curr_row_width >= self.MAX_WIDTH):
                            self.curr_row_width = 0
                            ln=1
                        else:
                            ln=0                            
                        self.pdf.cell(w=value, h=5, border=1, txt=data, ln=ln, align=align)
                    except:
                        self.curr_row_width = 0
                        print("error")
            else:
                self.pdf.cell(w=0, h=5, border=1, txt=data, ln=1, align='L')


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

