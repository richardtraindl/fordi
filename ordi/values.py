

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


"""LABOR_REFERENZ = {
    "** KATZE **";1
    "Gluc (71-148)";2
    "Bun (17-33)";3
    "Crea (0,8-1,8)";4
    "Phos (2,6-6)";5
    "GPT (22-84)";6
    "GOT (18-51)";7
    "Bil (0,1-0,4)";8
    "Lip (-40)";9
    "ALP (9-118)";10
    "Amyl (200-1900)";11
    "CK (97-309)";12
    "K (3,4-4,6)";13
    "TP (5,7-7,8)";14
    "T4 (8-50)";15
    "WBC (5-11)";16
    "RBC (5-10)";17
    "HK (27-47)";18
    "Hb (8-17)";19
    "Gran (3-12)";20
    "Lym (1-4)";21
    "Mon (0-0,5)";22
    "PLT (180-430)";23
    "Ka (3,4-4,6)";24
    "Na (147-156)";25
    "Cl (107-120)";26
    "** HUND **";100
    "Gluc (75-128)";101
    "Bun (9-29)";110
    "Crea (0,4-1,4)";120
    "Phos (1,9-5)";122
    "GPT (17-78)";123
    "GOT (17-44)";124
    "GGT (5-14)";125
    "Bil (0,1-0,5)";126
    "ALP (13-109)";127
    "K (3,8-5,0)";129
    "TP (5,0-7,2)";130
    "cPL (<200)";134
    "Fos (9,3-23,8)";135
    "VitB12 (234-812)";136
    "cTLI (8,5-35)";137
    "Cort (0,9-4,5)";138
    "WBC (6-12)";147
    "RBC (6-9)";148
    "HK (40-55)";149
    "Hb (15-19)";150
    "Gran (1,2-6,8)";165
    "Lym (1,2-3,2)";166
    "Mon (0,3-0,8)";167
    "PLT (150-500)";168
    "Ka (3,8-5,0)";169
    "Na (141-152)";170
    "Cl (102-117)";180
    "T4 (1,0-4,0)";181
    "TSH (<0,5)";182
    "Lip (10-160)";128
    "** KANINCHEN **";200
    "Leukos (5-12)";201
    "HK (33-48)";202
    "Gluc (115-214)";203
    "Bun (11-28)";204
    "Crea (0,6-1,4)";205
    "GPT (12-72)";206
    "GGT (5-18)";207
    "Bil (0,1-0,4)";208
    "ALP (21-75)";209
    "TP (4,9-6,9)";210
    "Calc (12,-14,5)";211
}"""


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

