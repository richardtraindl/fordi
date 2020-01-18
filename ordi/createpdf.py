
import os
from flask import render_template
from fpdf import FPDF, HTMLMixin


PDF_DIR_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdf')

class HTML2PDF(FPDF, HTMLMixin):
    pass

class CustomPDF(HTML2PDF):
    def header(self):
        # Set up a logo
        self.image('/home/richard/dev/flask/fordi/ordi/static/img/logo.png', 10, 8, 33)

        self.set_font('Arial', 'B', 15)

        # Add an address
        self.cell(100)
        self.cell(0, 5, 'Mike Driscoll', ln=1)
        self.cell(100)
        self.cell(0, 5, '123 American Way', ln=1)
        self.cell(100)
        self.cell(0, 5, 'Any Town, USA', ln=1)

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
    pdf.output('/home/richard/html2pdf.pdf')
    #file = open('/home/richard/html2pdf.pdf', 'w')
    #file.write()
    #file.close()


#from flask_wkhtmltopdf import Wkhtmltopdf
#app = Flask(__name__)
#app.config['WKHTMLTOPDF_BIN_PATH'] = r"/usr/bin/wkhtmltopdf" # r"C:\\EProg\\wkhtmltopdf\\bin
#app.config['PDF_DIR_PATH'] =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdf')
#wkhtmltopdf = Wkhtmltopdf(app)
#return wkhtmltopdf.render_template_to_pdf('ordi/prints/print_behandlungsverlauf.html', download=True, save=False, behandlungsverlauf=behandlungsverlauf, tierhaltung=tierhaltung, adresse=adresse)




def render_behandlungsverlauf_pdf(behandlungsverlauf, tierhaltung, adresse):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Welcome to Python!", ln=1, align="C")
    pdf.output("simple_demo.pdf")    
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    #pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    # fpdf.FPDF_FONTPATH = '/path/to/system/fonts'

    
    html = render_template('ordi/prints/print_behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, tierhaltung=tierhaltung, adresse=adresse)
    srcfilename = os.path.join(PDF_DIR_PATH, 'behandlungsverlauf.html')
    dstfilename = os.path.join(PDF_DIR_PATH, 'behandlungsverlauf.pdf')
    exefilename = os.path.join(WKHTMLTOPDF_BIN_PATH, 'wkhtmltopdf') # .exe
    file = open(srcfilename, 'w')
    file.write(html)
    file.close()
    header_opt = " --header-html " + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'ordi', 'prints', 'header.html') + " "
    footer_opts = " --disable-smart-shrinking --footer-html " + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'ordi', 'prints', 'footer.html') + " "
    cmd = WKHTMLTOPDF_BIN_PATH + header_opt + " " + footer_opts + " " + srcfilename + " " + dstfilename
    print(cmd)
    os.system(cmd)

    # image(name, x = None, y = None, w = 0, h = 0, type = '', link = '')
def add_image(image_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.image(image_path, x=10, y=8, w=100)
    pdf.set_font("Arial", size=12)
    pdf.ln(85)  # move 85 down
    pdf.cell(200, 10, txt="{}".format(image_path), ln=1)
    pdf.output("add_image.pdf")

def multipage_simple():
    pdf = FPDF()
    pdf.set_font("Arial", size=12)
    pdf.add_page()
    line_no = 1
    for i in range(100):
        pdf.cell(0, 10, txt="Line #{}".format(line_no), ln=1)
        line_no += 1
    pdf.output("multipage_simple.pdf")


 
def create_pdf(pdf_path):
    pdf = CustomPDF()
    # Create the special value {nb}
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    line_no = 1
    for i in range(50):
        pdf.cell(0, 10, txt="Line #{}".format(line_no), ln=1)
        line_no += 1
    pdf.output(pdf_path)

def header(self):
    # Set up a logo
    self.image('snakehead.jpg', 10, 8, 33)
    self.set_font('Arial', 'B', 15)
 
    # Add an address
    self.cell(100)
    self.cell(0, 5, 'Mike Driscoll', ln=1)
    self.cell(100)
    self.cell(0, 5, '123 American Way', ln=1)
    self.cell(100)
    self.cell(0, 5, 'Any Town, USA', ln=1)
 
    # Line break
    self.ln(20)

def create_pdf(pdf_path):
    pdf = CustomPDF()
    # Create the special value {nb}
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    line_no = 1
    for i in range(50):
        pdf.cell(0, 10, txt="Line #{}".format(line_no), ln=1)
        line_no += 1
    pdf.output(pdf_path)

def simple_table(spacing=1):
    data = [['First Name', 'Last Name', 'email', 'zip'],
            ['Mike', 'Driscoll', 'mike@somewhere.com', '55555'],
            ['John', 'Doe', 'jdoe@doe.com', '12345'],
            ['Nina', 'Ma', 'inane@where.com', '54321']
            ]
 
    pdf = FPDF()
    pdf.set_font("Arial", size=12)
    pdf.add_page()
 
    col_width = pdf.w / 4.5
    row_height = pdf.font_size
    for row in data:
        for item in row:
            pdf.cell(col_width, row_height*spacing,
                     txt=item, border=1)
        pdf.ln(row_height*spacing)
 
    pdf.output('simple_table.pdf')

 
def simple_table_html():
    pdf = HTML2PDF()
 
    table = """<table border="0" align="center" width="50%">
    <thead><tr><th width="30%">Header 1</th><th width="70%">header 2</th></tr></thead>
    <tbody>
    <tr><td>cell 1</td><td>cell 2</td></tr>
    <tr><td>cell 2</td><td>cell 3</td></tr>
    </tbody>
    </table>"""
 
    pdf.add_page()
    pdf.write_html(table)
    pdf.output('simple_table_html.pdf')



