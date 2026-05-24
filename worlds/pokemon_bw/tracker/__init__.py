
def range_incl(a: int, b: int) -> range:
    return range(a, b+1)


mapping_single: dict[int, int] = {
    317: 1,          # => "route1"
    319: 2,          # => "route2"
    321: 3,          # => "route3"
    326: 4,          # => "route4"
    329: 5,          # => "route5"
    331: 6,          # => "route6"
    337: 7,          # => "route7"
    345: 8,          # => "route8"
    348: 9,          # => "route9"
    355: 10,         # => "route10"
    365: 11,         # => "route11"
    368: 12,         # => "route12"
    370: 13,         # => "route13"
    374: 14,         # => "route14"
    378: 15,         # => "route15"
    383: 16,         # => "route16"
    397: 17,         # => "accumulatown"
    418: 18,         # => "anvilletown"
    28: 19,          # => "casteliacity"
    96: 20,          # => "driftveilcity"
    113: 21,         # => "icirruscity"
    406: 22,         # => "lacunosatown"
    107: 23,         # => "mistraltoncity_b"
    107 + 1024: 24,  # => "mistraltoncity_w"
    16: 25,          # => "nacrenecity"
    62: 26,          # => "nimbasacity"
    64: 27,          # => "nimbasacityeast"
    389: 28,         # => "nuvematown"
    120: 29,         # => "opelucidcity_b"
    120 + 1024: 30,  # => "opelucidcity_w"
    6: 31,           # => "striatoncity"
    412: 32,         # => "undellatown"
    376: 33,         # => "abundantshrine"
    246: 35,         # => "abyssalruins2f"
    247: 36,         # => "abyssalruins3f"
    248: 37,         # => "abyssalruins4f"
    338: 38,         # => "celestialtower1f"
    339: 39,         # => "celestialtower2f"
    340: 40,         # => "celestialtower3f"
    341: 41,         # => "celestialtower4f"
    342: 42,         # => "celestialtower5f"
    352: 43,         # => "challengerscave1f"
    353: 44,         # => "challengerscaveb1f"
    354: 45,         # => "challengerscaveb2f"
    195: 46,         # => "chargestonecave1f"
    196: 47,         # => "chargestonecaveb1f"
    197: 48,         # => "chargestonecaveb2f"
    194: 49,         # => "chargestonecaveoutside"
    192: 50,         # => "coldstorage"
    193: 51,         # => "coldstoragecontainer"
    191: 52,         # => "coldstorageoutside"
    158: 53,         # => "desertresort"
    157: 4,          # => "desertresortentrance" but it's on route 4 now
    207: 54,         # => "dragonspiraltower1f"
    208: 55,         # => "dragonspiraltower2f"
    209: 56,         # => "dragonspiraltower3f"
    210: 57,         # => "dragonspiraltower4f"
    211: 58,         # => "dragonspiraltower5f"
    212: 59,         # => "dragonspiraltower6f"
    213: 60,         # => "dragonspiraltower7f"
    205: 61,         # => "dragonspiraltowerentrance"
    206: 62,         # => "dragonspiraltoweroutside"
    152: 63,         # => "dreamyard"
    153: 64,         # => "dreamyardbasement"
    231: 65,         # => "giantchasmcave"
    232: 66,         # => "giantchasmcrater"
    233: 66,         # => "giantchasmcrater"
    234: 67,         # => "giantchasmdepths"
    230: 68,         # => "giantchasmentrance"
    335: 69,         # => "guidancechamber"
    235: 70,         # => "libertygarden"
    236: 71,         # => "libertygardenlighthouse"
    237: 71,         # => "libertygardenlighthousebasement" fused with lighthouse
    385: 72,         # => "lostlornforest"
    263: 73,         # => "marvelousbridge"
    333: 74,         # => "mistraltoncave1f"
    334: 75,         # => "mistraltoncave2f"
    346: 76,         # => "mooroficirrus"
    264: 77,         # => "nscastle1f"
    265: 78,         # => "nscastle2f"
    268: 78,         # => "nscastle2frightroom"
    269: 79,         # => "nscastle3f"
    271: 79,         # => "nscastle3fcenterroom"
    272: 79,         # => "nscastle3fleftroom"
    273: 80,         # => "nscastle4f"
    275: 80,         # => "nscastle4fcenterroom"
    274: 80,         # => "nscastlensroom"
    277: 81,         # => "nscastle5f"
    278: 82,         # => "nscastlethroneroom"
    155: 83,         # => "pinwheelforest"
    154: 84,         # => "pinwheelforestoutside"
    160: 85,         # => "reliccastle1f"
    161: 86,         # => "reliccastleb1f"
    162: 87,         # => "reliccastleb2f"
    163: 88,         # => "reliccastleb3f"
    164: 89,         # => "reliccastleb4f"
    165: 90,         # => "reliccastleb5f"
    166: 91,         # => "reliccastleb7f"
    190: 93,         # => "reliccastletower1f"
    189: 94,         # => "reliccastletowerb1f"
    188: 95,         # => "reliccastletowerb2f"
    187: 96,         # => "reliccastletowerb3f"
    186: 97,         # => "reliccastletowerb4f"
    185: 98,         # => "reliccastletowerb5f"
    184: 99,         # => "reliccastletowerb6f"
    183: 100,        # => "reliccastletowerb7f"
    182: 101,        # => "reliccastlevolcaronasroom"
    156: 102,        # => "ruminationfield"
    249: 103,        # => "skyarrowbridge"
    250: 103,        # => "skyarrowbridge"
    254: 104,        # => "tubelinebridge"
    199: 105,        # => "twistmountain"
    203: 106,        # => "twistmountainicerockcave"
    202: 107,        # => "twistmountainlowerlevel"
    201: 108,        # => "twistmountainmiddlelevel"
    198: 109,        # => "twistmountainoutside"
    200: 110,        # => "twistmountainupperlevel"
    240: 111,        # => "undellabay"
    222: 112,        # => "victoryroad1f leftmostroom"
    215: 112,        # => "victoryroad1f middleroom"
    220: 112,        # => "victoryroad1f rightmostroom"
    216: 113,        # => "victoryroad2f leftroom"
    219: 113,        # => "victoryroad2f rightroom"
    223: 114,        # => "victoryroad3f leftmostroom"
    217: 114,        # => "victoryroad3f middleroom"
    221: 114,        # => "victoryroad3f rightmostroom"
    224: 115,        # => "victoryroad4f leftmostroom"
    218: 115,        # => "victoryroad4f middleroom"
    227: 115,        # => "victoryroad4f rightmostroom"
    225: 116,        # => "victoryroad5f"
    226: 117,        # => "victoryroad6f"
    228: 118,        # => "victoryroad7f"
    214: 119,        # => "victoryroadoutside"
    229: 120,        # => "victoryroadtrialchamber"
    255: 121,        # => "villagebridge"
    324: 122,        # => "wellspringcave1f"
    325: 123,        # => "wellspringcaveb1f"
    423: 124,        # => "route17" these all are merged to one map
    387: 124,        # => "route18" these all are merged to one map
    238: 124,        # => "p2 lab" these all are merged to one map
    146: 125,        # => "pokemonleague"
    144: 126,        # => "pokemonleaguechampionsroom"
    145: 0,          # => "halloffame", overwold"
}

mapping_range: dict[range, int] = {
    range_incl(356, 364): 0,  # BADGE GATES, overworld
    range_incl(30, 40): 19,  # => "casteliacity"
    range_incl(136, 143): 125,  # POKÉMON LEAGUE
    range_incl(241, 245): 34,  # => "abyssalruins1f"
    range_incl(167, 181): 92,  # => "reliccastlemaze"
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
