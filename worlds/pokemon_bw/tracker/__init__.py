
def range_incl(a: int, b: int) -> range:
    return range(a, b+1)


mapping_single: dict[int, int] = {
    317: 1,  # => "route1"
    319: 2,  # => "route2"
    321: 3,  # => "route3"
    326: 4,  # => "route4"
    329: 5,  # => "route5"
    331: 6,  # => "route6"
    337: 7,  # => "route7"
    345: 8,  # => "route8"
    348: 9,  # => "route9"
    355: 10,  # => "route10"
    365: 11,  # => "route11"
    368: 12,  # => "route12"
    370: 13,  # => "route13"
    374: 14,  # => "route14"
    378: 15,  # => "route15"
    383: 16,  # => "route16"
    397: 19,  # => "accumulatown"
    418: 20,  # => "anvilletown"
    28: 22,  # => "casteliacity"
    96: 23,  # => "driftveilcity"
    113: 24,  # => "icirruscity"
    406: 25,  # => "lacunosatown"
    107: 26,  # => "mistraltoncity_b"
    107 + 1024: 27,  # => "mistraltoncity_w"
    16: 28,  # => "nacrenecity"
    62: 29,  # => "nimbasacity"
    64: 30,  # => "nimbasacityeast"
    389: 31,  # => "nuvematown"
    120: 32,  # => "opelucidcity_b"
    120 + 1024: 33,  # => "opelucidcity_w"
    6: 34,  # => "striatoncity"
    412: 35,  # => "undellatown"
    376: 37,  # => "abundantshrine"
    246: 39,  # => "abyssalruins2f"
    247: 40,  # => "abyssalruins3f"
    248: 41,  # => "abyssalruins4f"
    338: 42,  # => "celestialtower1f"
    339: 43,  # => "celestialtower2f"
    340: 44,  # => "celestialtower3f"
    341: 45,  # => "celestialtower4f"
    342: 46,  # => "celestialtower5f"
    352: 47,  # => "challengerscave1f"
    353: 48,  # => "challengerscaveb1f"
    354: 49,  # => "challengerscaveb2f"
    195: 50,  # => "chargestonecave1f"
    196: 51,  # => "chargestonecaveb1f"
    197: 52,  # => "chargestonecaveb2f"
    194: 53,  # => "chargestonecaveoutside"
    192: 54,  # => "coldstorage"
    193: 55,  # => "coldstoragecontainer"
    191: 56,  # => "coldstorageoutside"
    158: 57,  # => "desertresort"
    157: 58,  # => "desertresortentrance"
    207: 59,  # => "dragonspiraltower1f"
    208: 60,  # => "dragonspiraltower2f"
    209: 61,  # => "dragonspiraltower3f"
    210: 62,  # => "dragonspiraltower4f"
    211: 63,  # => "dragonspiraltower5f"
    212: 64,  # => "dragonspiraltower6f"
    213: 65,  # => "dragonspiraltower7f"
    205: 66,  # => "dragonspiraltowerentrance"
    206: 67,  # => "dragonspiraltoweroutside"
    152: 68,  # => "dreamyard"
    153: 69,  # => "dreamyardbasement"
    253: 0,  # DRIFTVEIL DRAWBRIDGE, overworld
    231: 70,  # => "giantchasmcave"
    232: 71,  # => "giantchasmcrater"
    233: 71,  # => "giantchasmcrater"
    234: 72,  # => "giantchasmdepths"
    230: 73,  # => "giantchasmentrance"
    335: 74,  # => "guidancechamber"
    235: 75,  # => "libertygarden"
    236: 76,  # => "libertygardenlighthouse"
    237: 77,  # => "libertygardenlighthousebasement"
    385: 78,  # => "lostlornforest"
    263: 79,  # => "marvelousbridge"
    333: 80,  # => "mistraltoncave1f"
    334: 81,  # => "mistraltoncave2f"
    346: 82,  # => "mooroficirrus"
    264: 83,  # => "nscastle1f"
    265: 84,  # => "nscastle2f"
    268: 85,  # => "nscastle2frightroom"
    269: 86,  # => "nscastle3f"
    271: 87,  # => "nscastle3fcenterroom"
    272: 88,  # => "nscastle3fleftroom"
    273: 89,  # => "nscastle4f"
    275: 90,  # => "nscastle4fcenterroom"
    277: 91,  # => "nscastle5f"
    274: 92,  # => "nscastlensroom"
    278: 93,  # => "nscastlethroneroom"
    155: 95,  # => "pinwheelforest"
    154: 96,  # => "pinwheelforestoutside"
    160: 97,  # => "reliccastle1f"
    161: 98,  # => "reliccastleb1f"
    162: 99,  # => "reliccastleb2f"
    163: 100,  # => "reliccastleb3f"
    164: 101,  # => "reliccastleb4f"
    165: 102,  # => "reliccastleb5f"
    166: 103,  # => "reliccastleb7f"
    190: 105,  # => "reliccastletower1f"
    189: 106,  # => "reliccastletowerb1f"
    188: 107,  # => "reliccastletowerb2f"
    187: 108,  # => "reliccastletowerb3f"
    186: 109,  # => "reliccastletowerb4f"
    185: 110,  # => "reliccastletowerb5f"
    184: 111,  # => "reliccastletowerb6f"
    183: 112,  # => "reliccastletowerb7f"
    182: 113,  # => "reliccastlevolcaronasroom"
    156: 114,  # => "ruminationfield"
    249: 115,  # => "skyarrowbridge"
    250: 115,  # => "skyarrowbridge"
    254: 116,  # => "tubelinebridge"
    199: 117,  # => "twistmountain"
    203: 118,  # => "twistmountainicerockcave"
    202: 119,  # => "twistmountainlowerlevel"
    201: 120,  # => "twistmountainmiddlelevel"
    198: 121,  # => "twistmountainoutside"
    200: 122,  # => "twistmountainupperlevel"
    240: 123,  # => "undellabay"
    222: 124,  # => "victoryroad1fleftmostroom"
    215: 125,  # => "victoryroad1fmiddleroom"
    220: 126,  # => "victoryroad1frightmostroom"
    216: 127,  # => "victoryroad2fleftroom"
    219: 128,  # => "victoryroad2frightroom"
    223: 129,  # => "victoryroad3fleftmostroom"
    217: 130,  # => "victoryroad3fmiddleroom"
    221: 131,  # => "victoryroad3frightmostroom"
    224: 132,  # => "victoryroad4fleftmostroom"
    218: 133,  # => "victoryroad4fmiddleroom"
    227: 134,  # => "victoryroad4frightmostroom"
    225: 135,  # => "victoryroad5f"
    226: 136,  # => "victoryroad6f"
    228: 137,  # => "victoryroad7f"
    214: 138,  # => "victoryroadoutside"
    229: 139,  # => "victoryroadtrialchamber"
    255: 140,  # => "villagebridge"
    324: 141,  # => "wellspringcave1f"
    325: 142,  # => "wellspringcaveb1f"
    423 : 143, # => "route17" these all are merged to one map
    387: 143, # => "route18" these all are merged to one map
    238: 143, # => "p2 lab" these all are merged to one map
}

mapping_range: dict[range, int] = {
    range_incl(356, 364): 0,  # BADGE GATES, overworld
    range_incl(30, 40): 22,  # => "casteliacity"
    range_incl(136, 146): 0,  # POKÉMON LEAGUE, overworld
    range_incl(241, 245): 38,  # => "abyssalruins1f"
    range_incl(167, 181): 104,  # => "reliccastlemaze"
}


def should_change(map_id: int) -> bool:
    if map_id in mapping_single:
        return True
    for rang in mapping_range:
        if map_id in rang:
            return True
    return False


def map_page_index(data: int) -> int:
    if data in mapping_single:
        return mapping_single[data]
    for rang in mapping_range:
        if data in rang:
            return mapping_range[rang]
    return 0
