

ANREDE = {
    ''       : 0,
    'Herr'   : 1,
    'Frau'   : 2,
    'Famlie' : 3,
    'Firma'  : 4
}


GESCHLECHT = {
    ''   : 0,
    'm'  : 1,
    'mk' : 2,
    'w'  : 3,
    'wk' : 4
}


KONTAKT = {
    ''        : 0,
    'Telefon' : 1,
    'Fax'     : 2,
    'E-Mail'  : 3
}


LABOR_REFERENZ = [
    "** KATZE **",
    "Gluc (71-148)",
    "Bun (17-33)",
    "Crea (0,8-1,8)",
    "Phos (2,6-6)",
    "GPT (22-84)",
    "GOT (18-51)",
    "Bil (0,1-0,4)",
    "Lip (-40)",
    "ALP (9-118)",
    "Amyl (200-1900)",
    "CK (97-309)",
    "K (3,4-4,6)",
    "TP (5,7-7,8)",
    "T4 (8-50)",
    "WBC (5-11)",
    "RBC (5-10)",
    "HK (27-47)",
    "Hb (8-17)",
    "Gran (3-12)",
    "Lym (1-4)",
    "Mon (0-0,5)",
    "PLT (180-430)",
    "Ka (3,4-4,6)",
    "Na (147-156)",
    "Cl (107-120)",
    "** HUND **",
    "Gluc (75-128)",
    "Bun (9-29)",
    "Crea (0,4-1,4)",
    "Phos (1,9-5)",
    "GPT (17-78)",
    "GOT (17-44)",
    "GGT (5-14)",
    "Bil (0,1-0,5)",
    "ALP (13-109)",
    "K (3,8-5,0)",
    "TP (5,0-7,2)",
    "cPL (<200)",
    "Fos (9,3-23,8)",
    "VitB12 (234-812)",
    "cTLI (8,5-35)",
    "Cort (0,9-4,5)",
    "WBC (6-12)",
    "RBC (6-9)",
    "HK (40-55)",
    "Hb (15-19)",
    "Gran (1,2-6,8)",
    "Lym (1,2-3,2)",
    "Mon (0,3-0,8)",
    "PLT (150-500)",
    "Ka (3,8-5,0)",
    "Na (141-152)",
    "Cl (102-117)",
    "T4 (1,0-4,0)",
    "TSH (<0,5)",
    "Lip (10-160)",
    "** KANINCHEN **",
    "Leukos (5-12)",
    "HK (33-48)",
    "Gluc (115-214)",
    "Bun (11-28)",
    "Crea (0,6-1,4)",
    "GPT (12-72)",
    "GGT (5-18)",
    "Bil (0,1-0,4)",
    "ALP (21-75)",
    "TP (4,9-6,9)",
    "Calc (12,-14,5)" ]


IMPFUNG = {
    'RC'         : 22,
    'RCP'        : 1,
    'FIP'        : 3,
    'Leukose'    : 2,
    'RCP Ch'     : 14,
    'SHLP'       : 6,
    'SHLPT'      : 21,
    'SHLPPi'     : 7,
    'SHLPPiT'    : 8,
    'L4'         : 18,
    'Lepto'      : 13,
    'TW1'        : 4,
    'TW2'        : 15,
    'TW3'        : 20,
    'Merilym3'   : 19,
    'Bbpi'       : 10,
    'Myxo'       : 11,
    'RHD'        : 12,
    'SP'         : 5,
    'SHP'        : 17,
    'FIP2'       : 16,
    'Borreliose' : 9
}


ARTIKEL = {
    ''                       : 0,
    'Visite'                 : 1,
    'Labor'                  : 2,
    'Injektion'              : 3,
    'Röntgen'                : 4,
    'Ultraschall'            : 5,
    'Medikamente'            : 6,
    'Futter und Medikamente' : 7,
    'Artikel mit 20%'        : 8,
    'Artikel mit 13%'        : 9,
    'Artikel mit 10%'        : 10
}

ARTIKEL_STEUER = {
    ARTIKEL['Visite']                 : 20.00,
    ARTIKEL['Labor']                  : 20.00,
    ARTIKEL['Injektion']              : 20.00,
    ARTIKEL['Röntgen']                : 20.00,
    ARTIKEL['Ultraschall']            : 20.00,
    ARTIKEL['Medikamente']            : 10.00,
    ARTIKEL['Futter und Medikamente'] : 13.00,
    ARTIKEL['Artikel mit 20%']        : 20.00,
    ARTIKEL['Artikel mit 13%']        : 13.00,
    ARTIKEL['Artikel mit 10%']        : 10.00
}

