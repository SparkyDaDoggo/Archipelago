
from typing import TYPE_CHECKING, Coroutine, Any, Callable
import worlds._bizhawk as bizhawk

if TYPE_CHECKING:
    from ..bizhawk_client import PokemonBWClient
    from worlds._bizhawk.context import BizHawkClientContext


def get_method(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> Callable[
    ["PokemonBWClient", "BizHawkClientContext"], Coroutine[Any, Any, bool]
]:

    match ctx.slot_data["options"]["goal"]:
        case "ghetsis":
            return defeat_ghetsis
        case "champion":
            return become_champion
        case "cynthia":
            return defeat_cynthia
        case "cobalion":
            return encounter_cobalion
        # case "regional_pokedex":
        # case "national_pokedex":
        # case "custom_pokedex":
        case "tmhm_hunt":
            return verify_tms_hms
        case "seven_sages_hunt":
            return find_seven_sages
        case "legendary_hunt":
            return encounter_legendaries
        case "pokemon_master":
            return do_everything
        case _:
            client.logger.warning("Bad goal in slot data: "+ctx.slot_data["options"]["goal"])
            return error


async def defeat_ghetsis(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return client.flags_cache[0x1D3//8] & 8 != 0


async def become_champion(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return client.flags_cache[0x1D4//8] & 16 != 0


async def defeat_cynthia(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + client.var_offset + (2 * 0xE4), 1, client.ram_read_write_domain),
        )
    )
    return read[0][0] >= 2


async def encounter_cobalion(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return client.flags_cache[649//8] & 2 != 0


async def verify_tms_hms(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return client.flags_cache[0x191//8] & 2 != 0


async def find_seven_sages(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + client.var_offset + (2 * 0xCC), 1, client.ram_read_write_domain),
        )
    )
    return read[0][0] >= 6 and client.flags_cache[2400//8] & 1 != 0


async def encounter_legendaries(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> bool:
    return (
        client.flags_cache[649//8] & 2 != 0 and  # Cobalion
        client.flags_cache[650//8] & 4 != 0 and  # Terrakion
        client.flags_cache[651//8] & 8 != 0 and  # Virizion
        client.flags_cache[801//8] & 2 != 0 and  # Kyurem
        client.flags_cache[779//8] & 8 != 0 and  # Victini
        client.flags_cache[810//8] & 4 != 0 and  # Volcarona
        client.flags_cache[0x1CE//8] & 64 != 0  # Reshiram/Zekrom
    )


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
