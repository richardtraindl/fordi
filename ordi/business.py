
from .values import *


class cCalc:
    def __init__(self, brutto_summe=0, netto_summe=0, steuerbetrag_zwanzig=0, steuerbetrag_dreizehn=0, steuerbetrag_zehn=0):
        self.brutto_summe = brutto_summe
        self.netto_summe = netto_summe
        self.steuerbetrag_zwanzig = steuerbetrag_zwanzig
        self.steuerbetrag_dreizehn = steuerbetrag_dreizehn
        self.steuerbetrag_zehn = steuerbetrag_zehn
        self.error_msg = ""


def calc_rechnung(rechnungszeilen):
    calc = cCalc()

    if(len(rechnungszeilen) == 0):
        calc.error_msg = "Mindestens eine Rechnungszeile erforderlich."
        return calc

    for rechnungszeile in rechnungszeilen:
        try:
            artikelcode = int(rechnungszeile[1])
            steuersatz = ARTIKEL_STEUER[artikelcode]
        except:
            calc.error_msg = "Falsche Artikelart."
            return calc

        try:
            str_betrag = rechnungszeile[3].replace(",", ".")
            betrag = float(str_betrag)
            betrag = round(betrag, 2)
        except:
            calc.error_msg = "Betrag ist keine Zahl."
            return calc

        calc.brutto_summe += betrag
        nettobetrag = round(betrag * 100 / (100 + steuersatz))
        if(steuersatz == 20):
            calc.steuerbetrag_zwanzig += (betrag - nettobetrag)
        elif(steuersatz == 13):
            calc.steuerbetrag_dreizehn += (betrag - nettobetrag)
        else: # steuersatz == 10
            calc.steuerbetrag_zehn += (betrag - nettobetrag)

    calc.netto_summe = calc.brutto_summe - (calc.steuerbetrag_zwanzig + calc.steuerbetrag_dreizehn + calc.steuerbetrag_zehn)
    return calc

