
from typing import TYPE_CHECKING, Coroutine, Any, Callable

if TYPE_CHECKING:
    from ..bizhawk_client import PokemonBWClient
    from worlds._bizhawk.context import BizHawkClientContext


def get_method(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> Callable[
    ["PokemonBWClient", "BizHawkClientContext"], Coroutine[Any, Any, bool]
]:

    all_goals = []
    if isinstance(ctx.slot_data["options"]["goal"], list):
        goals_list = ctx.slot_data["options"]["goal"]
    else:
        goals_list = [ctx.slot_data["options"]["goal"]]
    for goal in goals_list:
        match goal:
            case "ghetsis":
                all_goals.append(defeat_ghetsis)
            case "champion":
                all_goals.append(become_champion)
            case "cynthia":
                all_goals.append(defeat_cynthia)
            case "cobalion":
                all_goals.append(encounter_cobalion)
            # case "regional_pokedex":
            # case "national_pokedex":
            # case "custom_pokedex":
            case "tmhm_hunt":
                all_goals.append(verify_tms_hms)
            case "seven_sages_hunt":
                all_goals.append(find_seven_sages)
            case "legendary_hunt":
                all_goals.append(encounter_legendaries)
            case "pokemon_master":
                all_goals.append(do_everything)
            case _:
                client.logger.warning("Bad goal in slot data: "+goal)
                all_goals.append(error)
    if len(all_goals) == 1:
        return all_goals[0]
    else:
        async def combined_goals(_client: "PokemonBWClient", _ctx: "BizHawkClientContext") -> bool:
            for _g in all_goals:
                if not await _g(_client, _ctx):
                    return False
            return True
        return combined_goals


async def defeat_ghetsis(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return client.get_flag(0x1D3)


async def become_champion(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return client.get_flag(0x1D4)


async def defeat_cynthia(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return (await client.read_var(ctx, 0xE4)) >= 2


async def encounter_cobalion(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return client.get_flag(649)


async def verify_tms_hms(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return client.get_flag(0x191)


async def find_seven_sages(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return (await client.read_var(ctx, 0xCC)) >= 6 and await defeat_ghetsis(client, ctx)


async def encounter_legendaries(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return client.get_flag(0x1EA)


async def do_everything(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return (
        await defeat_ghetsis(client, ctx) and
        await become_champion(client, ctx) and
        await defeat_cynthia(client, ctx) and
        await encounter_cobalion(client, ctx) and
        await verify_tms_hms(client, ctx) and
        await find_seven_sages(client, ctx) and
        await encounter_legendaries(client, ctx)
    )


async def error(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return False
