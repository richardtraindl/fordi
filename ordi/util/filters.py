

from ..values import ANREDE, GESCHLECHT, KONTAKT
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

