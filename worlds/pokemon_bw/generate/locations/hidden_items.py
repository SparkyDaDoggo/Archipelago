from typing import TYPE_CHECKING

from ...locations import PokemonBWLocation
from ...data import AccessRule, ExtendedRule, ExtRulesTuple, AndExtRules as AND

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region


def lookup(domain: int) -> dict[str, int]:
    from ...data.locations.ingame_items.hidden_items import table, seasonal

    return {name: data.flag_id + domain for tab in (table, seasonal) for name, data in tab.items()}


def create(world: "PokemonBWWorld") -> None:
    from ...data.locations.ingame_items.hidden_items import table, seasonal

    dowsing_machine_rule: "AccessRule" = lambda state: state.has_any(("Dowsing Machine", "Out of logic"), world.player)
    f_cache = {}

    def f(ext_rule: ExtendedRule | ExtRulesTuple) -> "AccessRule":
        rule = world.rules_dict.get_or_add(ext_rule)
        if rule not in f_cache:
            f_cache[rule] = lambda state: rule(state) and dowsing_machine_rule(state)
        return f_cache[rule]

    for tab in (table, seasonal):
        for name, data in tab.items():
            if data.inclusion_rule is None or data.inclusion_rule(world):
                r: "Region" = world.regions[data.region]
                l: PokemonBWLocation = PokemonBWLocation(world.player, name, world.location_name_to_id[name], r)
                l.progress_type = data.progress_type(world)
                if world.options.modify_logic.is_require_dowsing:
                    if data.rule is not None:
                        l.access_rule = f(data.rule)
                    else:
                        l.access_rule = dowsing_machine_rule
                else:
                    if data.rule is not None:
                        l.access_rule = world.rules_dict.get_or_add(data.rule)
                r.locations.append(l)
