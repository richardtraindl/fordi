
import os
from flask import (render_template)

WKHTMLTOPDF_BIN_PATH = r"C:\\EProg\\wkhtmltopdf\\bin"
PDF_DIR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdf')

def render_behandlungsverlauf_pdf(behandlungsverlauf, tierhaltung, adresse):
    html = render_template('ordi/prints/print_behandlungsverlauf.html', behandlungsverlauf=behandlungsverlauf, tierhaltung=tierhaltung, adresse=adresse)
    srcfilename = os.path.join(PDF_DIR_PATH, 'behandlungsverlauf.html')
    dstfilename = os.path.join(PDF_DIR_PATH, 'behandlungsverlauf.pdf')
    exefilename = os.path.join(WKHTMLTOPDF_BIN_PATH, 'wkhtmltopdf.exe')
    file = open(srcfilename, 'w')
    file.write(html)
    file.close()
    header_opt = " --header-html c:\\wse4\\flask\\ordi\\templates\\ordi\\prints\\header.html "
    footer_opts = " --disable-smart-shrinking --footer-html c:\\wse4\\flask\\ordi\\templates\\ordi\\prints\\footer.html "
    cmd = exefilename + header_opt + " " + footer_opts + " " + srcfilename + " " + dstfilename
    print(cmd)
    os.system(cmd)
