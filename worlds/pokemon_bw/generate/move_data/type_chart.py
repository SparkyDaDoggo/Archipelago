from typing import TYPE_CHECKING
from ...options.moves import PlandoTypeEffect

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def randomize_type_chart(world: "PokemonBWWorld") -> dict[tuple[str, str], int]:
    from ...data.pokemon.types import by_name, chart

    this_chart = {(t, tt): 0xff for t in by_name for tt in by_name}

    mods = world.options.randomize_type_chart

    for name, plando in world.options.move_data_plando:
        if isinstance(plando, PlandoTypeEffect):
            name: str
            plando: PlandoTypeEffect
            split = name.index("_")
            this_chart[name[:split], name[split+1:]] = plando.effectiveness

    if mods.is_shuffle:
        weak, resist, immune = 0, 0, 0
        for matchup, effect in chart.items():
            weak += effect == 8
            resist += effect == 2
            immune += effect == 0
        for matchup, effect in this_chart.items():
            if effect != 0xff:
                weak -= effect == 8
                resist -= effect == 2
                immune -= effect == 0
        weak = max(weak, 0) if not mods.is_disable_weaknesses else 0
        resist = max(resist, 0) if not mods.is_disable_resistances else 0
        immune = max(immune, 0) if not mods.is_disable_immunities else 0
        to_fill = [matchup for matchup, effect in this_chart.items() if effect != 0xff]
        world.random.shuffle(to_fill)
        for matchup in to_fill[:weak]:
            this_chart[matchup] = 8
        for matchup in to_fill[weak:weak+resist]:
            this_chart[matchup] = 2
        for matchup in to_fill[weak+resist:weak+resist+immune]:
            this_chart[matchup] = 0
        for matchup in to_fill[weak+resist+immune:]:
            this_chart[matchup] = 4
    elif mods.is_randomize:
        possible = (4,
                    8 if not mods.is_disable_weaknesses else 4,
                    2 if not mods.is_disable_resistances else 4,
                    0 if not mods.is_disable_immunities else 4)
        for matchup, effect in this_chart.items():
            if effect != 0xff:
                continue
            this_chart[matchup] = world.random.choice(possible)

    return this_chart
