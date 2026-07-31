from .. import EggGroupData

groups: dict[str, EggGroupData] = {
    "Monster": EggGroupData(1, ("Normal", "Flying", "Poison", "Ground", "Rock", "Bug", "Steel", "Ice", "Dragon", "Dark")),
    "Water 1": EggGroupData(2, ("Water", "Ice")),
    "Bug": EggGroupData(3, ("Flying", "Poison", "Bug", "Grass")),
    "Flying": EggGroupData(4, ("Flying", "Dragon")),
    "Field": EggGroupData(5, None),
    "Fairy": EggGroupData(6, ("Normal", "Flying", "Electric", "Psychic")),
    "Grass": EggGroupData(7, ("Bug", "Grass")),
    "Human-Like": EggGroupData(8, ("Normal", "Fighting", "Ghost", "Psychic")),
    "Water 3": EggGroupData(9, ("Water", "Ice")),
    "Mineral": EggGroupData(10, ("Poison", "Ground", "Rock", "Steel", "Ice")),
    "Amorphous": EggGroupData(11, ("Fighting", "Poison", "Ground", "Rock", "Ghost", "Steel", "Psychic", "Dark")),
    "Water 2": EggGroupData(12, ("Water", "Ice")),
    "Ditto": EggGroupData(13, None),
    "Dragon": EggGroupData(14, ("Normal", "Flying", "Poison", "Fire", "Ice", "Dragon")),
    "Unknown": EggGroupData(15, None),
}
