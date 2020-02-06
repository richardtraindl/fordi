

from datetime import date
from ..values import ANREDE, GESCHLECHT, KONTAKT, ARTIKEL
from .helper import reverse_lookup


def mapanrede(anredecode):
    anrede = reverse_lookup(ANREDE, anredecode)
    if(anrede == None):
        anrede = ""
    return anrede


def mapgeschlecht(geschlechtscode):
    geschlecht = reverse_lookup(GESCHLECHT, geschlechtscode)
    if(geschlecht == None):
        geschlecht = ""
    return geschlecht


def mapkontakt(kontaktcode):
    kontakt = reverse_lookup(KONTAKT, kontaktcode)
    if(kontakt == None):
        kontakt = ""
    return kontakt


def mapartikel(artikelcode):
    artikel = reverse_lookup(ARTIKEL, artikelcode)
    if(artikel == None):
        artikel = ""
    return artikel


def filter_supress_none(val):
    if not val is None:
        return val
    else:
        return ''

