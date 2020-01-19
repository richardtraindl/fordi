
import os
from flask import render_template
from fpdf import FPDF, HTMLMixin


PDF_DIR_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdf')

class HTML2PDF(FPDF, HTMLMixin):
    pass

class CustomPDF(HTML2PDF):
    def header(self):
        # Set up a logo
        self.image(name=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img', 'logo.png'), x=173, y=10, h=24) 

        self.set_font('Arial', '', 11)
        self.cell(112)
        self.cell(w=50, h=4, txt='', ln=1)

        # Add an address
        self.set_font('Arial', '', 11)
        self.cell(112)
        text1 = 'TIERARZTPRAXIS'
        self.cell(w=50, h=4, txt=text1, ln=1, align='C')
        
        self.set_font('Arial', 'U', 11)
        self.cell(112)
        text2 = 'Kaiserstrasse'
        self.cell(w=50, h=4, txt=text2, ln=1, align='C')

        self.set_font('Arial', '', 11)
        self.cell(112)
        self.cell(w=50, h=2, txt='', ln=1)

        self.set_font('Arial', '', 11)
        self.cell(112)
        text3 = 'Dr. Elfriede Koppensteiner'
        self.cell(w=50, h=4, txt=text3, ln=1, align='R')

        self.cell(112)
        text4 = 'Mag. Gerold Koppensteiner'
        self.cell(w=50, h=4, txt=text4, ln=1, align='R')

         # Line break
        self.ln(20)
 
    def footer(self):
        self.set_y(-10)

        self.set_font('Arial', '', 10)

        # Add a page number
        kontakt = '1070 Tierarztpraxis Kaiserstrasse, Tel. 01 944 5 944, 0699 1 944 5 944 ATU 56934599'
        self.cell(0, 5, kontakt, 0, 0, 'L')


def html2pdf(html):
    pdf = CustomPDF()
    pdf.add_page()
    pdf.write_html(html)
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', 'output.pdf')
    pdf.output(filename)
