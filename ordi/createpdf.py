
import os, copy
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
            #print(styledefs)
            for styledef in styledefs:
                styledef = "".join(styledef.split()) #remove whitespace
                keyval = styledef.split(":")         #split into css-attribute and css-attribute-value
                if(len(keyval) == 2):
                    if(keyval[0] == attribute):
                        return keyval[1]
    return None


def isblock(tag):
    return (tag != "br" and tag != "hr" and tag != "span")


class cTag:
    def __init__(self, tag, attrs, parent, fpdf):
        self.tag = tag
        self.attrs = attrs

        if(isblock(tag) and parent):
            self.x = parent.x
            self.width = parent.width
        else:
            self.x = fpdf.x
            self.width = 0

        self.y = fpdf.y
        self.page = fpdf.page_no()
        self.maxy = fpdf.y
        self.maxpage = fpdf.page_no()
        self.grid_items_cnt = None

        if(parent):
            attribute = find(attrs, "display")
            if(attribute and attribute == "grid"):
                self.grid_items_cnt = 0

            parent_attr = find(parent.attrs, "display")
            if(parent_attr and parent_attr == "grid" and parent.grid_items_cnt != None):
                str_columns = find(parent.attrs, "grid-template-columns")
                if(str_columns):
                    columns = str_columns.strip('mm').split('mm')
                    startx = parent.x
                    idx = 0
                    for column in columns:
                        if(idx < parent.grid_items_cnt):
                            startx += int(column)
                        else:
                            self.width = int(column)
                            break
                        idx += 1
                    self.x = startx
                    self.y = parent.y
                    self.page = parent.page
                    parent.grid_items_cnt += 1
                    if(parent.grid_items_cnt >= len(columns)):
                        parent.y = fpdf.y
                        parent.page = fpdf.page_no()
                        parent.maxy = fpdf.y
                        parent.maxpage = fpdf.page_no()
                        parent.grid_items_cnt = 0

    def prnt(self, fpdf, data):
        print(self.tag, "width: ", str(self.width), "x: ", str(self.x))
        if(self.width != 0):
            fpdf.x = self.x
            fpdf.y = self.y
            fpdf.page = self.page
 
        align = 'L'
        text_align_value = find(self.attrs, "text-align")
        if(text_align_value):
            if(text_align_value == "center"):
                align = 'C'
            elif(text_align_value == "right"):
                align = 'R'

        if(isblock(self.tag)):
            fpdf.multi_cell(w=self.width, h=4, border=1, txt=data, align=align)
            return

        if(self.tag == "br"):
            fpdf.cell(w=0, h=4, border=0, txt="", ln=1, align=align)
            return

        if(self.tag == "hr"):
            max_width = 210 - (fpdf.l_margin + fpdf.r_margin)
            fpdf.line(fpdf.x, fpdf.y, (fpdf.l_margin + max_width), fpdf.y)
            return

        if(self.tag == "span"):
            fpdf.multi_cell(w=0, h=4, border=0, txt=data, align=align)
            return

        fpdf.multi_cell(w=self.width, h=4, border=1, txt=data, align=align)


class MyHTMLParser(HTMLParser):
    def __init__(self, fpdf):
        super().__init__()

        self.fpdf = fpdf

        self.tags = []


    def handle_starttag(self, tag, attrs):
        #print("<", tag)

        if(self.tags):
            parent = self.tags[-1]
        else:
            parent = None

        if(tag != "br" and tag != "hr"):
            ctag = cTag(tag, attrs, parent, self.fpdf)
            self.tags.append(ctag)
            if(tag == "section" or tag == "div" or tag == "p"):
                padding_top_value = find(attrs, "padding-top")
                if(padding_top_value):
                    try:
                        value = int(padding_top_value.strip('mm'))
                        self.fpdf.cell(w=0, h=value, border=0, txt="", ln=1, align="L")
                    except:
                        print("error")


    def handle_endtag(self, tag):
        #print("-", tag, ">")
        if(tag != "br" and tag != "hr"):
            current = self.tags.pop()
            if(tag == "section" or tag == "div" or tag == "p"):
                padding_bottom_value = find(current.attrs, "padding-bottom")
                if(padding_bottom_value):
                    try:
                        value = int(padding_bottom_value.strip('mm'))
                        self.fpdf.cell(w=0, h=value, border=0, txt="", ln=1, align="L")
                    except:
                        print("error")

                if(self.tags):
                    parent = self.tags[-1]
                    if(isblock(parent.tag)):
                        display_value = find(parent.attrs, "display")
                        if(display_value and display_value == "grid"):
                            str_columns = find(parent.attrs, "grid-template-columns")
                            if(str_columns):
                                if(parent.maxpage < self.fpdf.page_no() or
                                   (parent.maxpage == self.fpdf.page_no() and
                                    parent.maxy < self.fpdf.y)):
                                    parent.maxy = self.fpdf.y
                                    parent.maxpage = self.fpdf.page_no()
                                else:
                                    self.fpdf.y = parent.maxy
                                    self.fpdf.page = parent.maxpage


    def handle_data(self, data):
        #print("Encountered some data  :", str(len(data)) + " " + data)

        data = data.strip()
        if(len(data) > 0 and self.tags):
            ctag = self.tags[-1]
            ctag.prnt(self.fpdf, data)


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
    fpdf.set_font('Arial', '', 11)
    fpdf.add_page()
    
    parser = MyHTMLParser(fpdf)
    parser.feed(html)
    fpdf.output(path_and_filename)

