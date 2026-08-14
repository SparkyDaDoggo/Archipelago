
def get_item_groups() -> dict[str, set[str]]:
    from .data.items import main_items, key_items, tm_hm, medicine, berries, badges, seasons

    return {
        "TMs": set(tm_hm.tm),
        "HMs": set(tm_hm.hm),
        "TMs and HMs": {*tm_hm.tm, *tm_hm.hm},
        "Main items": {*main_items.filler, *main_items.fossils, *main_items.min_once,
                       *main_items.mail, *main_items.unused},
        "Fossils": set(main_items.fossils),
        "Key items": {*key_items.progression, *key_items.vanilla, *key_items.useless, *key_items.special},
        "Medicine": {*medicine.table, *medicine.important},
        "Berries": {*berries.standard, *berries.niche},
        "Badges": set(badges.table),
        "Seasons": set(seasons.table),
    }


def get_location_groups() -> dict[str, set[str]]:
    from .data.locations import dexsanity, countsanity, shinysanity
    from .data.locations.ingame_items import overworld_items, hidden_items, other, special

    return {
        "Dexsanity": set(dexsanity.location_table),
        "Dexcountsanity": set(countsanity.dexcountsanity),
        "Shinysanity": set(shinysanity.location_table),
        "Shinycountsanity": set(countsanity.shinycountsanity),
        "Overworld items": {*overworld_items.table, *overworld_items.abyssal_ruins, *overworld_items.seasonal},
        "Abyssal Ruins items": set(overworld_items.abyssal_ruins),
        "Hidden items": {*hidden_items.table, *hidden_items.seasonal},
        "NPC items": {*other.table, *other.seasonal, *special.gym_badges, *special.gym_tms, *special.tm_hm_ncps},
        "Season-dependant items": {*overworld_items.seasonal, *hidden_items.seasonal, *other.seasonal},
        "Badge rewards": set(special.gym_badges),
        "Gym TM rewards": set(special.gym_tms),
        "TM/HM locations": {*special.gym_tms, *special.tm_hm_ncps},
        "Post-Ghetsis locations": {
            "Relic Castle - 1F towerside item", "Relic Castle - B3F towerside hidden item",
            "Nuvema Town - Item from Looker after beating Ghetsis", "Desert Resort - Item from Professor Juniper",
            "Twist Mountain - Item from worker near ice rock cave", "Route 18 - TM from sage Rood",
            "Relic Castle - TM from sage Ryoku", "Cold Storage - TM from sage Zinzolin",
            "Chargestone Cave - TM from sage Bronius",
        },
    }
