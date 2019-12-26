

from ..values import ANREDE, GESCHLECHT, KONTAKT
from .helper import reverse_lookup


def mapanrede(anredecode):
    return reverse_lookup(ANREDE, anredecode)

def mapgeschlecht(geschlechtscode):
    return reverse_lookup(GESCHLECHT, geschlechtscode)

def mapkontakt(kontaktcode):
    return reverse_lookup(KONTAKT, kontaktcode)