from .. import EggGroupData

groups: dict[str, EggGroupData] = {
    "Monster": EggGroupData(1, True, ("Normal", "Flying", "Poison", "Ground", "Rock", "Bug", "Steel", "Ice", "Dragon", "Dark")),
    "Water 1": EggGroupData(2, True, ("Water", "Ice")),
    "Bug": EggGroupData(3, True, ("Flying", "Poison", "Bug", "Grass")),
    "Flying": EggGroupData(4, True, ("Flying", "Dragon")),
    "Field": EggGroupData(5, True, None),
    "Fairy": EggGroupData(6, True, ("Normal", "Flying", "Electric", "Psychic")),
    "Grass": EggGroupData(7, True, ("Bug", "Grass")),
    "Human-Like": EggGroupData(8, True, ("Normal", "Fighting", "Ghost", "Psychic")),
    "Water 3": EggGroupData(9, True, ("Water", "Ice")),
    "Mineral": EggGroupData(10, True, ("Poison", "Ground", "Rock", "Steel", "Ice")),
    "Amorphous": EggGroupData(11, True, ("Fighting", "Poison", "Ground", "Rock", "Ghost", "Steel", "Psychic", "Dark")),
    "Water 2": EggGroupData(12, True, ("Water", "Ice")),
    "Ditto": EggGroupData(13, True, None),
    "Dragon": EggGroupData(14, True, ("Normal", "Flying", "Poison", "Fire", "Ice", "Dragon")),
    "Unknown": EggGroupData(15, True, None),
    "Static": EggGroupData(32, False, ("Steel", "Electric")),
}
