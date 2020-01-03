
from . import values.py


def calc_rechnung(rechnungzeilen)
    brutto_summe = 0
    netto_summe = 0
    steuerbetrag_zwanzig = 0
    steuerbetrag_dreizehn = 0
    steuerbetrag_zehn = 0

    for rechnungzeile in rechnungzeilen:
        brutto_summe += rechnungzeile.betrag
        steuersatz = ARTIKEL_STEUER[rechnungzeile.artikelartcode]
        nettobetrag += rechnungzeile.betrag * 100 / (100 + steuersatz)
        if(steuersatz == 20):
            steuerbetrag_zwanzig += (rechnungzeile.betrag - nettobetrag)
        elif(steuersatz == 13):
            steuerbetrag_dreizehn += (rechnungzeile.betrag - nettobetrag)
        else: # steuersatz == 10
            steuerbetrag_zehn += (rechnungzeile.betrag - nettobetrag)

    netto_summe = brutto_summe - (steuerbetrag_zwanzig + steuerbetrag_dreizehn + steuerbetrag_zehn)
    return round(brutto_summe, 2), round(netto_summe, 2), round(steuerbetrag_zwanzig, 2), round(steuerbetrag_dreizehn, 2), round(steuerbetrag_zehn, 2)

