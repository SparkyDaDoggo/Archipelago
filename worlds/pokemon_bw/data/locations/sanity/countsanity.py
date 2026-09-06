
dexcountsanity: dict[str, int] = {
    f"Pokédex - Catch {count} Pokémon": count for count in range(1, 650)
}

seencountsanity: dict[str, int] = {
    f"Pokédex - See {count} Pokémon": count for count in range(1, 650)
}

formcountsanity: dict[str, int] = {
    f"Pokédex - See {count} alternate forms": count for count in range(1, 66)
}

# gendercountsanity: dict[str, int] = {
#     f"Pokédex - See {count} {g} Pokémon": count for g in ("male", "female") for count in range(1, 650)
# } | {
#     f"Pokédex - See {count} gendered Pokémon": count for count in range(1, 1299)
# }

shinycountsanity: dict[str, int] = {
    f"Pokédex - Find {count} shiny Pokémon": count for count in range(1, 650)
}

shinyformcountsanity: dict[str, int] = {
    f"Pokédex - Find {count} alternate shiny forms": count for count in range(1, 66)
}

# shinygendercountsanity: dict[str, tuple[int, str]] = {
#     f"Pokédex - See {count} shiny {g} Pokémon": (count, g) for g in ("male", "female") for count in range(1, 650)
# } | {
#     f"Pokédex - See {count} shiny gendered Pokémon": (count, "any") for count in range(1, 1299)
# }
