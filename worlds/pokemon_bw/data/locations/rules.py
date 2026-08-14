from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from .. import ExtendedRule, InclusionRule, AccessRule
from ..pokemon.species import forms_by_dex
from ..items import tm_hm

if TYPE_CHECKING:
    from ... import PokemonBWWorld

# Item requirements

can_use_strength: ExtendedRule = lambda state, world: (
    state.has("HM04 Strength", world.player)
    and state.has_any(world.strength_species, world.player)
)

can_use_surf: ExtendedRule = lambda state, world: (
    state.has("HM03 Surf", world.player)
    and state.has_any(world.surf_species, world.player)
)

can_use_cut: ExtendedRule = lambda state, world: (
    state.has("HM01 Cut", world.player)
    and state.has_any(world.cut_species, world.player)
)

can_use_waterfall: ExtendedRule = lambda state, world: (
    can_use_surf(state, world)
    and state.has("HM05 Waterfall", world.player)
    and state.has_any(world.waterfall_species, world.player)
)

can_use_dive: ExtendedRule = lambda state, world: (
    can_use_surf(state, world)
    and state.has("HM06 Dive", world.player)
    and state.has_any(world.dive_species, world.player)
)

can_use_flash: ExtendedRule = lambda state, world: (
    state.has("TM70 Flash", world.player)
    and state.has_any(world.flash_species, world.player)
)

can_use_fly: ExtendedRule = lambda state, world: (
    state.has("HM02 Fly", world.player)
    and state.has_any(world.fly_species, world.player)
)

can_fish: ExtendedRule = lambda state, world: state.has("Super Rod", world.player)
has_rage_candy_bar: ExtendedRule = lambda state, world: state.has("Rage Candy Bar", world.player)
has_basement_key: ExtendedRule = lambda state, world: state.has("Basement Key", world.player)
has_parcel: ExtendedRule = lambda state, world: state.has("Parcel", world.player)
has_loot_sack: ExtendedRule = lambda state, world: state.has("Loot Sack", world.player)
has_dragon_skull: ExtendedRule = lambda state, world: state.has("Dragon Skull", world.player)
has_liberty_pass: ExtendedRule = lambda state, world: state.has("Liberty Pass", world.player)
has_machine_part: ExtendedRule = lambda state, world: state.has("Machine Part", world.player)
has_explorer_kit: ExtendedRule = lambda state, world: state.has("Explorer Kit", world.player)
has_tidal_bell: ExtendedRule = lambda state, world: state.has("Tidal Bell", world.player)
has_oaks_letter: ExtendedRule = lambda state, world: state.has("Oak's Letter", world.player)
has_blue_card: ExtendedRule = lambda state, world: state.has("Blue Card", world.player)
has_red_chain: ExtendedRule = lambda state, world: state.has("Red Chain", world.player)
has_any_legendary_stone: ExtendedRule = lambda state, world: state.has_any(("Light Stone", "Dark Stone"), world.player)
has_lock_capsule: ExtendedRule = lambda state, world: state.has("Lock Capsule", world.player)
has_all_grams: ExtendedRule = lambda state, world: state.has_all(("Wingull Gram 1", "Wingull Gram 2", "Wingull Gram 3"), world.player)
has_gb_player: ExtendedRule = lambda state, world: state.has("GB Sounds", world.player)
has_all_tms_hms: ExtendedRule = lambda state, world: state.has_all(tm_hm.tm, world.player) and state.has_all(tm_hm.hm, world.player)

has_root_fossil: ExtendedRule = lambda state, world: state.has("Root Fossil", world.player)
has_claw_fossil: ExtendedRule = lambda state, world: state.has("Claw Fossil", world.player)
has_helix_fossil: ExtendedRule = lambda state, world: state.has("Helix Fossil", world.player)
has_dome_fossil: ExtendedRule = lambda state, world: state.has("Dome Fossil", world.player)
has_old_amber: ExtendedRule = lambda state, world: state.has("Old Amber", world.player)
has_armor_fossil: ExtendedRule = lambda state, world: state.has("Armor Fossil", world.player)
has_skull_fossil: ExtendedRule = lambda state, world: state.has("Skull Fossil", world.player)
has_cover_fossil: ExtendedRule = lambda state, world: state.has("Cover Fossil", world.player)
has_plume_fossil: ExtendedRule = lambda state, world: state.has("Plume Fossil", world.player)


# Badge requirements

has_trio_badge: ExtendedRule = lambda state, world: state.has("Trio Badge", world.player)
has_basic_badge: ExtendedRule = lambda state, world: state.has("Basic Badge", world.player)
has_insect_badge: ExtendedRule = lambda state, world: state.has("Insect Badge", world.player)
has_bolt_badge: ExtendedRule = lambda state, world: state.has("Bolt Badge", world.player)
has_quake_badge: ExtendedRule = lambda state, world: state.has("Quake Badge", world.player)
has_jet_badge: ExtendedRule = lambda state, world: state.has("Jet Badge", world.player)
has_freeze_badge: ExtendedRule = lambda state, world: state.has("Freeze Badge", world.player)
has_legend_badge: ExtendedRule = lambda state, world: state.has("Legend Badge", world.player)


# Season requirements

can_set_winter: ExtendedRule = lambda state, world: (
    world.options.season_control == "vanilla" or (
        state.can_reach_region("Nimbasa City", world.player) and (
            world.options.season_control == "changeable" or state.has("Winter", world.player)
        )
    )
)

can_set_autumn: ExtendedRule = lambda state, world: (
    world.options.season_control == "vanilla" or (
        state.can_reach_region("Nimbasa City", world.player) and (
            world.options.season_control == "changeable" or state.has("Autumn", world.player)
        )
    )
)

can_set_summer: ExtendedRule = lambda state, world: (
    world.options.season_control == "vanilla" or (
        state.can_reach_region("Nimbasa City", world.player) and (
            world.options.season_control == "changeable" or state.has("Summer", world.player)
        )
    )
)

can_set_spring: ExtendedRule = lambda state, world: (
    world.options.season_control == "vanilla" or (
        state.can_reach_region("Nimbasa City", world.player) and (
            world.options.season_control == "changeable" or state.has("Spring", world.player)
        )
    )
)

can_set_other_than_winter: ExtendedRule = lambda state, world: (
    world.options.season_control == "vanilla" or (
        state.can_reach_region("Nimbasa City", world.player) and (
            world.options.season_control == "changeable" or state.has_any(("Spring", "Summer", "Autumn"), world.player)
        )
    )
)

can_catch_all_deerlings: ExtendedRule = lambda state, world: (
    (
        not world.options.randomize_wild_pokemon.is_randomize
        and world.options.season_control == "vanilla"
    )
    or state.has_all((
        "Deerling (Spring)", "Deerling (Summer)", "Deerling (Autumn)", "Deerling (Winter)"
    ), world.player)
)

encounter_can_set_spring: ExtendedRule = lambda state, world: (
    state.can_reach_region("Nimbasa City", world.player) and (
        world.options.season_control == "changeable" or state.has("Spring", world.player)
    )
)

encounter_can_set_summer: ExtendedRule = lambda state, world: (
    state.can_reach_region("Nimbasa City", world.player) and (
        world.options.season_control == "changeable" or state.has("Summer", world.player)
    )
)

encounter_can_set_autumn: ExtendedRule = lambda state, world: (
    state.can_reach_region("Nimbasa City", world.player) and (
        world.options.season_control == "changeable" or state.has("Autumn", world.player)
    )
)

encounter_can_set_winter: ExtendedRule = lambda state, world: (
    state.can_reach_region("Nimbasa City", world.player) and (
        world.options.season_control == "changeable" or state.has("Winter", world.player)
    )
)

# Event requirements

has_visited_biancas_house: ExtendedRule = lambda state, world: state.has("[Event] Argument in Bianca's house", world.player)
has_seen_accumula_speech: ExtendedRule = lambda state, world: state.has("[Event] Accumula Town Ghetsis speech", world.player)
has_fought_cheren_trainerschool: ExtendedRule = lambda state, world: state.has("[Event] Trainers' School Cheren fight", world.player)
has_fought_plasma_wellspring: ExtendedRule = lambda state, world: state.has("[Event] Wellspring Cave Plasma fight", world.player)
has_helped_man_nimbasa: ExtendedRule = lambda state, world: state.has("[Event] Helping old man in Nimbasa", world.player)
has_encountered_cobalion: ExtendedRule = lambda state, world: state.has("[Event] Encounter Cobalion", world.player)
has_confronted_plasma_castelia: ExtendedRule = lambda state, world: state.has("[Event] Castelia Plasma Hideout confrontation", world.player)
has_confronted_plasma_cold_storage: ExtendedRule = lambda state, world: state.has("[Event] Cold Storage Plasma confrontation", world.player)
has_battled_n_chargestone: ExtendedRule = lambda state, world: state.has("[Event] Defeating N Chargestone", world.player)
has_rung_bell_celestial: ExtendedRule = lambda state, world: state.has("[Event] Ring bell Celestial Tower", world.player)
has_talked_drayden_iris: ExtendedRule = lambda state, world: state.has("[Event] Talk with Iris and Drayden", world.player)
has_released_roamer: ExtendedRule = lambda state, world: state.has("[Event] Released roamer", world.player)
has_introduced_junipers_lab: ExtendedRule = lambda state, world: state.has("[Event] Introduction in Juniper's Lab", world.player)
has_fought_plasma_dreamyard: ExtendedRule = lambda state, world: state.has("[Event] Dreamyard North Plasma fight", world.player)
has_confronted_ghetsis_relic_castle: ExtendedRule = lambda state, world: state.has("[Event] Relic Castle Ghetsis confrontation", world.player)
has_fought_castelia_dancers: ExtendedRule = lambda state, world: state.has_all((
    "[Event] Defeating Catelia Dancer Mickey", "[Event] Defeating Catelia Dancer Raymond", "[Event] Defeating Catelia Dancer Edmond", ), world.player)
has_found_woman_on_village_bridge: ExtendedRule = lambda state, world: state.has("[Event] Talking to Patrat woman Village Bridge", world.player)
has_talked_wingull_route_13: ExtendedRule = lambda state, world: state.has("[Event] Talked to girl next to Wingull Route 13", world.player)
has_heard_weather_route_10: ExtendedRule = lambda state, world: state.has("[Event] Heard weather warning route 10 gate", world.player)
has_talked_to_kids_mistralton: ExtendedRule = lambda state, world: state.has("[Event] Talked with kids Mistralton", world.player)

has_defeated_striaton_gym: ExtendedRule = lambda state, world: state.has("[Event] Defeating Leader Cilan/Chili/Cress", world.player)
has_defeated_nacrene_gym: ExtendedRule = lambda state, world: state.has("[Event] Defeating leader Lenora", world.player)
has_defeated_driftveil_gym: ExtendedRule = lambda state, world: state.has("[Event] Defeating leader Clay", world.player)
has_defeated_mistralton_gym: ExtendedRule = lambda state, world: state.has("[Event] Defeating leader Skyla", world.player)
has_defeated_icirrus_gym: ExtendedRule = lambda state, world: state.has("[Event] Defeating leader Brycen", world.player)
has_defeated_opelucid_gym: ExtendedRule = lambda state, world: state.has("[Event] Defeating leader Iris/Drayden", world.player)
has_defeated_elite_four: ExtendedRule = lambda state, world: state.has_all((
    "[Event] Defeating elite four Shauntal", "[Event] Defeating elite four Marshal",
    "[Event] Defeating elite four Grimsley", "[Event] Defeating elite four Caitlin", ), world.player)
has_beaten_ghetsis: ExtendedRule = lambda state, world: state.has("[Event] Defeating Ghetsis", world.player)

has_access_magnetic_area: ExtendedRule = lambda state, world: state.has("[Event] Magnetic Area", world.player)
has_access_moss_rock: ExtendedRule = lambda state, world: state.has("[Event] Moss Rock", world.player)
has_access_ice_rock: ExtendedRule = lambda state, world: state.has("[Event] Ice Rock", world.player)
has_access_move_relearner: ExtendedRule = lambda state, world: state.has("[Event] Access to move relearner", world.player)
has_access_friendship_checker: ExtendedRule = lambda state, world: state.has("[Event] Access to friendship checker", world.player)
has_access_castelia_evo_items: ExtendedRule = lambda state, world: state.has("[Event] Castelia evo items", world.player)
has_access_chargestone_evo_items: ExtendedRule = lambda state, world: state.has("[Event] Chargestone evo items", world.player)
has_access_twist_evo_items: ExtendedRule = lambda state, world: state.has("[Event] Twist Mountain evo items", world.player)
has_access_mall_evo_items: ExtendedRule = lambda state, world: state.has("[Event] Shopping Mall Nine evo items", world.player)
has_access_r10_evo_items: ExtendedRule = lambda state, world: state.has("[Event] Route 10 evo items", world.player)
has_access_undella_evo_items: ExtendedRule = lambda state, world: state.has("[Event] Undella evo items", world.player)
has_access_chasm_evo_items: ExtendedRule = lambda state, world: state.has("[Event] Giant Chasm evo items", world.player)

# has_aaaaaaaaaaaaa: ExtendedRule = lambda state, world: state.has("[Event] AAAAAAAAAAAAAAA", world.player)
# has_aaaaaaaaaaaaa: ExtendedRule = lambda state, world: state.has("[Event] AAAAAAAAAAAAAAA", world.player)
# has_aaaaaaaaaaaaa: ExtendedRule = lambda state, world: state.has("[Event] AAAAAAAAAAAAAAA", world.player)
# has_aaaaaaaaaaaaa: ExtendedRule = lambda state, world: state.has("[Event] AAAAAAAAAAAAAAA", world.player)


# Encounter requirements

def build_caught_ext_rule(x: int) -> ExtendedRule:
    def r(state: CollectionState, world: "PokemonBWWorld") -> bool:
        found: int = 0
        prog_items = state.prog_items[world.player]
        for forms_list in forms_by_dex.values():
            for form in forms_list:
                if prog_items[form]:
                    found += 1
                    break
            if found >= x:
                return True
        return False

    return r


def build_caught_rule(x: int, world: "PokemonBWWorld") -> AccessRule:
    def r(state: CollectionState) -> bool:
        found: int = 0
        prog_items = state.prog_items[world.player]
        for forms_list in forms_by_dex.values():
            for form in forms_list:
                if prog_items[form]:
                    found += 1
                    break
            if found >= x:
                return True
        return False

    return r


def build_seen_ext_rule(x: int) -> ExtendedRule:
    def r(state: CollectionState, world: "PokemonBWWorld") -> bool:
        if world.options.all_pokemon_seen:
            return True
        found: int = 0
        prog_items = state.prog_items[world.player]
        for forms_list in forms_by_dex.values():
            for form in forms_list:
                if prog_items[form]:
                    found += 1
                    break
            if found >= x:
                return True
        return False

    return r


has_forces_of_nature: ExtendedRule = lambda state, world: state.has_all(("Thundurus", "Tornadus"), world.player)
has_celebi: ExtendedRule = lambda state, world: state.has("Celebi", world.player)
has_legendary_beasts: ExtendedRule = lambda state, world: state.has_all(("Entei", "Raikou", "Suicune"), world.player)
has_genesect: ExtendedRule = lambda state, world: state.has("Genesect", world.player)
has_shaymin: ExtendedRule = lambda state, world: state.has("Shaymin", world.player)
has_other_locations_species: ExtendedRule = lambda state, world: state.has(world.other_locations_species, world.player)
has_25_species: ExtendedRule = build_seen_ext_rule(25)
has_51_species: ExtendedRule = build_seen_ext_rule(51)
has_60_species: ExtendedRule = build_seen_ext_rule(60)
has_115_species_seen: ExtendedRule = build_seen_ext_rule(115)


# Miscellaneous/mixed requirements

has_fighting_type_species: ExtendedRule = lambda state, world: (
    state.has_any(world.fighting_type_species, world.player)
)

dark_cave: ExtendedRule = lambda state, world: (
    not world.options.modify_logic.is_require_flash or can_use_flash(state, world)
    or state.has("Out of logic", world.player)
)
driftveil_random_tm: ExtendedRule = lambda state, world: (
    state.has_all((world.driftveil_random_tm, world.other_locations_species), world.player)
)
route_8_logic: ExtendedRule = lambda state, world: (
    can_use_surf(state, world) or (
        state.can_reach_region("Nimbasa City", world.player) and (
            world.options.season_control == "changeable" or state.has_any(("Spring", "Summer", "Autumn"), world.player)
        )
    )
)


# Encounter inclusion rules

vanilla_seasons: InclusionRule = lambda world: world.options.season_control == "vanilla"
changeable_seasons: InclusionRule = lambda world: world.options.season_control != "vanilla"
disabled: InclusionRule = lambda world: False
randomized_wild: InclusionRule = lambda world: world.options.randomize_wild_pokemon.is_randomize
tm_hm_hunt_goal: InclusionRule = lambda world: "tmhm_hunt" in (world.options.goal.combined or (world.options.goal.current_key, ))
# TODO properly implement when door shuffle
shuffled_doors: InclusionRule = lambda world: False and world.options.door_shuffle.any_shuffled()
vanilla_doors: InclusionRule = lambda world: True or not world.options.door_shuffle.any_shuffled()
