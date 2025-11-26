# Encounter Plando guide for Pokémon Black and White

## How does this work?

The Encounter Plando option in your yaml file lets you force place certain Pokémon species into certain slots.
Every encounter table (one for each map that has wild Pokémon) in the game contains 56 slots, 
grouped into different encounter methods (grass, surfing, etc.), 
with each slot containing the species, a minimum catch level, and a maximum catch level.
Every entry in your Encounter Plando option will place a specific species into one or more slots of an 
encounter method in an encounter table.
Encounter Plando entries take priority over wild Pokémon randomization and works regardless of whether 
you even have wild Pokémon randomized or not.

## Important notes for multiworld hosts

Encounter Plando can lead to generation failures that might not look like coming from this option. 
The Pokémon Black and White host.yaml settings have a toggle to enable or disable this option, 
which is by default set to true. 
If disabled, yamls with Encounter Plando entries will ignore them and just print a warning to the console 
without stopping multiworld genration.

## How do I use it?

Every entry consists of 3 to 5 arguments:
- `map` determines which map (i.e. which encounter table) this entry should be placed into. 
  You can find a list of all map names [here](encounter%20plando%20lists.md#all-map-names).
  The map names must match the names on that site exactly (except for casing).
- `seasons`/`season` is an optional argument that determines which season(s) this entry should be placed into. 
  However, not all maps support different encounters for different seasons. 
  You can find a list of all maps supporting different seasons 
  [here](encounter%20plando%20lists.md#maps-that-support-having-different-seasons).
  If the map does not support different seasons, you **have to omit** this argument.
  Else, you can either write a single season or a list of seasons.
- `method` determines which encounter method this entry should be placed into. 
  Allowed method names are `Grass`, `Dark grass`, `Rustling grass`, `Surfing`, `Surfing rippling`, 
  `Fishing`, and `Fishing rippling`.
  Note that the floor of caves/dungeons/etc. count as `Grass` and dust clouds 
  and flying Pokémon's shadows count as `Rustling grass`.
- `slots`/`slot` is an optional argument that determines the exact slot(s) of the entry in the specified method.
  You can either put in a single number, a list of numbers, or omit this argument.
  If omitted, this entry will be placed into all slots of the specified method.
  See [here](encounter%20plando%20lists.md#slot-values) for further information on allowed values.
- `species` determines which species should be placed into the specified slot(s).
  You can either put in a single species name or a list of species names.
  `None` can be used (preferably in lists) to make the generator not plando any species into the specified slot(s).
  If multiple species are provided, a random one out of them is chosen.
  Writing the same species multiple times is allowed and can increase its chance of being chosen over 
  the other species in the list.
  See [here](encounter%20plando%20lists.md#all-species-names) for a list of all species names.
  Note that different forms have different names, e.g. Unown (A)/(B)/...

Specifying a slot that does not exist in the game (e.g. `Grass` slots in Striaton City) will not have any effect
on the game since all encounter tables have space for each encounter method, 
but it will also not be considered in logic and give no warning or error message.

## An example on how using this option could look like

```
...

Pokemon Black and White:
  ...
  
  encounter_plando:
    - map: Route 1
      method: Grass
      species: Blastoise
    - map: Route 8
      season: Summer
      method: Surfing
      slot: 4
      species: Liligant
    - map: Twist Mountain (Upper Level)
      seasons:
        - Spring
        - Winter
      method: Grass
      slots:
        - 0
        - 2
        - 4
        - 6
        - 8
        - 10
      species:
        - Snorlax
        - Snorlax
        - Dragonite
        - Bidoof
        - None
        - None
```

# Custom encounter rates guide for Pokémon Black and White

## How does this work?

The base encounter rates for all wild encounter slots are (in %) usually [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1] 
for (Dark/Rustling) Grass, [60, 30, 5, 4, 1] for Surfing (Rippling), and [40, 40, 15, 4, 1] for Fishing (Rippling).
Using the `Modify Encounter Rates` option, you can change those rates to either a few preset rates, a random distribution,
or a custom list.

## How do I use it?

Instead of just writing a single option name like `vanilla` or `try_normalized`, you need to provide key-value pairs **as a choice**.
"As a choice" means that you'll need to pack it into a list or as a weighted choice, see the examples down below for how to do it.
To change (Dark/Rustling) Grass rates, use the `Grass` key. Surfing/Fishing (Rippling) rates need the `Surfing`/`Fishing` key respectively.
Though you are not required to always use all keys; you can leave any of them as vanilla if you want.
The value has to be a list of positive integers. The `Grass` key needs exactly 12 numbers, while the others need exactly 5 numbers.
All numbers in a list need to add up to exactly 100 and need to be greater than 0.

## Examples on how using this option could look like

```
...
Pokemon Black and White:
  ...
  modify_encounter_rates:
    # The extra "- " is required in order to not break weighting
    # That however makes picking out a random key-value pair possible (if multiple are provided)
    - Grass: [30, 10, 4, 2, 2, 2, 25, 10, 5, 4, 4, 2]
      Surfing: [25, 25, 30, 10, 10]
      Fishing: [96, 1, 1, 1, 1]
```

```
...
Pokemon Black and White:
  ...
  modify_encounter_rates:
    # Alternative way with different weights
    # Notice that leaving out the "Surfing" key is valid
    vanilla: 25
    {Grass: [30, 10, 4, 2, 2, 2, 25, 10, 5, 4, 4, 2], Fishing: [96, 1, 1, 1, 1]}: 75
```

# Text Plando guide for Pokémon Black and White (coming in 0.4.0)

## How does this work?

All ingame text in stored in text files that are structured like tables. The Text Plando option lets you fill 
these tables however you want. Every entry must follow a certain format that is adopted from the ALttP Text Plando.
This option takes priority over the `Funny Dialog` option.

## Important notes for multiworld hosts

Text Plando is a plando setting that is included in every host.yaml. It needs to be enabled in order for 
this option to work. If it is disabled, yamls with Text Plando entries will show a warning about the setting
being disabled and not check the provided entries for correct formatting.

## How do I use it?

Every entry contains 2 or 3 arguments:
- `text` defines the text you want to insert into the game.
  You will have to set every line break yourself and use the following commands:
  - `[NextLine]` is a simple line break and often used in combination with other commands.
  - `[Scroll]` makes the text box scroll the lines up by one. It is always followed by a `[NextLine]`.
  - `[End]` ends the current chain of lines, waits for any button press, and shows an arrow indicating that. 
    It is never used alone. If followed by a `[NextLine]`, it will clear the text box after any button press 
    and continues on the upper line. If followed by a `[Terminate]`, it will close the text box after any button press.
  - `[Terminate]` closes the text box. It has to be written at the end of **every** line and **only** 
    at the end of a line. If an `[End]` stands in front of it, it will first wait for any button press before closing.
    However, in case you haven't noticed, the game **always** waits for any button press before closing 
    almost any text box, but sometimes with an arrow indicating the wait for a button press and sometimes not.
    The arrow only appears when combined with an `[End]`. You always need to make sure you only and always use 
    an `[End]` when needed. If it is needed, and you omit it, the text box will close without any player interaction.
    If it's not required, and you add it, the game will wait for two button presses.
  - `[c_xxx_#x_x_...]` commands are various commands used for different purposes, e.g. displaying various names 
    with different formatting, forcing the text to be displayed faster, changing the text color, etc.
    The best way to learn what commands to use for your use case is by looking at already existing text lines.
  
  Since text boxes have limited width, it is recommended to make no line longer than 40 characters.
  Certain kinds of texts used in other places than text boxes (e.g. ability descriptions, pokédex entries, etc.)
  might have other additional restrictions.
- `at` defines where to put the given text. It consists of the section (currently only `system` and `story`),
  the file number (0-287 for system, 0-471 for story), the block (always 0, anything else will have no effect),
  and the line (with the first line having the number 0). All parts have to be separated by spaces (" ").
- `percentage` is an optional argument that can give every entry a chance of not being written to the rom.

You can extract the text files of a patched rom by enabling the `extract_text` setting in your host.yaml before
running your patch file. That will produce two text files (one for the system section and one for the story section)
that you can use to find where you have to place your text lines.

## An example on how using this option could look like

```
...
Pokemon Black and White:
  ...
  text_plando:
    - text: "Huh? Why did you press the[NextLine]B button?[Scroll][NextLine]It will stay weak![Terminate]"
      at: "system 172 0 1"
      percentage: 100
    - text: "[c_100_#1_0] received [c_101_#1_1]![End][NextLine]Congratulations![Terminate]"
      at: "story 160 0 7"
      percentage: 50
    - text: "The arch nemesis of every Nuzlocker.[Terminate]"
      at: "system 235 0 202"
```

# Modify Levels (advanced mode) guide for Pokémon Black and White (coming in 0.4.0)

## How does this work?

This option usually works like a simple counter. The webhost and any software that lets you edit yamls with a user
interface will show you the option as such. However, you can also provide multiple entries with multiple arguments
like you know it from most Plando options (if edited in a text editor). This "advanced" mode lets you chain multiple
calculations. This allows for more complex and interesting calculations.

## How do I use it?

Every entry contains the following 3 arguments:
- `type` is either `Trainer` or `Wild`.
- `mode` is either `Multiply`, `Add`, or `Power`. You can alternatively use the internal numbers 0-2 (accordingly).
- `value` is the value that should be used in the calculation. 
  The `Multiply` mode interprets it as a percentage and allows for values in range 1 to 10000. 
  The `Add` mode interprets it as whole levels and allows for values in range -99 to 99.
  The `Power` mode interprets it as a percentage and allows for values in range 1 to 700.

Do note that after every calculation, the result is rounded down and capped at 1 and 100

## An example on how using this option could look like

The following example flattens the level curve of earlygame trainers, but makes it steeper for lategame trainers,
while maintaining the minimum level of 5:
```
...
Pokemon Black and White:
  ...
  modify_levels:
    - type: Trainer
      mode: Add
      value: -4
    - type: Trainer
      mode: Power
      value: 110
    - type: Trainer
      mode: Multiply
      value: 67
    - type: Trainer
      mode: Add
      value: 4
```

Here's another example that sets the levels of all wild and trainer pokémon in the game to exactly 20:
```
...
Pokemon Black and White:
  ...
  modify_levels:
    - type: Trainer
      mode: Add
      value: -99
    - type: Trainer
      mode: Multiply
      value: 20
    - type: Wild
      mode: Add
      value: -99
    - type: Wild
      mode: Multiply
      value: 20
```
