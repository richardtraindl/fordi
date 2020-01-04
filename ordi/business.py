
from .values import *


def calc_rechnung(rechnungszeilen):
    brutto_summe = 0
    netto_summe = 0
    steuerbetrag_zwanzig = 0
    steuerbetrag_dreizehn = 0
    steuerbetrag_zehn = 0

    for rechnungszeile in rechnungszeilen:
        try:
            artikelartcode = int(rechnungszeile[1])
        except:
            continue
        try:
            str_betrag = rechnungszeile[3].replace(",", ".")
            betrag = float(str_betrag)
        except:
            continue
        brutto_summe += betrag
        steuersatz = ARTIKEL_STEUER[artikelartcode]
        nettobetrag = betrag * 100 / (100 + steuersatz)
        if(steuersatz == 20):
            steuerbetrag_zwanzig += (betrag - nettobetrag)
        elif(steuersatz == 13):
            steuerbetrag_dreizehn += (betrag - nettobetrag)
        else: # steuersatz == 10
            steuerbetrag_zehn += (betrag - nettobetrag)

    netto_summe = brutto_summe - (steuerbetrag_zwanzig + steuerbetrag_dreizehn + steuerbetrag_zehn)
    return round(brutto_summe, 2), round(netto_summe, 2), round(steuerbetrag_zwanzig, 2), round(steuerbetrag_dreizehn, 2), round(steuerbetrag_zehn, 2)

