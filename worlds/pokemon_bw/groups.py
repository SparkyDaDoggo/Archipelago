
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
    from .data.locations.sanity import countsanity, dexsanity, shinysanity, seensanity, formsanity, shinyformsanity
    from .data.locations.ingame_items import overworld_items, hidden_items, other, special
    from .options.sanity import DEXSANITYSANITY_ENABLED

    return {
        "Dexsanity": set(dexsanity.location_table),
        "Dexcountsanity": set(countsanity.dexcountsanity),
        "Seensanity": set(seensanity.location_table),
        "Seencountsanity": set(countsanity.seencountsanity) if DEXSANITYSANITY_ENABLED else set("Pokédex - Catch 1 Pokémon"),
        "Formsanity": set(formsanity.table),
        "Formcountsanity": set(countsanity.formcountsanity) if DEXSANITYSANITY_ENABLED else set("Pokédex - Catch 1 Pokémon"),
        "Shinysanity": set(shinysanity.location_table),
        "Shinycountsanity": set(countsanity.shinycountsanity) if DEXSANITYSANITY_ENABLED else set("Pokédex - Catch 1 Pokémon"),
        "Shinyformsanity": set(shinyformsanity.table) if DEXSANITYSANITY_ENABLED else set("Pokédex - Catch 1 Pokémon"),
        "Shinyformcountsanity": set(countsanity.shinyformcountsanity) if DEXSANITYSANITY_ENABLED else set("Pokédex - Catch 1 Pokémon"),
        "Overworld items": {*overworld_items.table, *overworld_items.abyssal_ruins, *overworld_items.seasonal},
        "Abyssal Ruins items": set(overworld_items.abyssal_ruins),
        "Hidden items": {*hidden_items.table, *hidden_items.seasonal},
        "NPC items": {*other.table, *other.seasonal, *special.gym_badges, *special.gym_tms, *special.tm_hm_ncps},
        "Season-dependant items": {*overworld_items.seasonal, *hidden_items.seasonal, *other.seasonal},
        "Badge rewards": set(special.gym_badges),
        "Gym TM rewards": set(special.gym_tms),
        "TM/HM locations": {*special.gym_tms, *special.tm_hm_ncps},
        # Leftover from before these were auto excluded, not removing it to prevent breaking old yamls
        # Also, having an empty group raises unittest failures
        "Post-Ghetsis locations": {"Nuvema Town - Item from Looker after beating Ghetsis"},
        "Show-a-pokémon locations": {
            "Route 6 - Item from scientist for all Deerling forms",
            "Pinwheel Forest Outside - Item from challenge rock",
            "Driftveil City - Item from lady asking for a pokémon knowing a certain TM move",
            "Icirrus City - Item from Pokémon Fan Club chairman for gaining 25 levels",
            "Icirrus City - Item from Pokémon Fan Club chairman for gaining 50 levels",
            "Lacunosa Town - Item from girl for showing a Shaymin",
            "P2 Laboratory - Item from scientist #1",
            "P2 Laboratory - Item from scientist #2",
            "Village Bridge - Item from fisherman for showing a certain pokémon caught today #1",
            "Village Bridge - Item from fisherman for showing a certain pokémon caught today #2",
            "Village Bridge - Item from fisherman for showing a certain pokémon caught today #3",
            "Village Bridge - Item from fisherman for showing a certain pokémon caught today #4",
            "Village Bridge - Item from fisherman for showing a certain pokémon caught today #5",
            "Castelia City - Item from harlequin in Studio Castelia",
        },
    }
