# Roadmap for Pokémon BW AP

The "barely working" version will still be playable to goal, so it will start with 0.1.0.

Most bigger features will increase the version by +0.1.
<br>However, do not confuse that with semantic version naming: `major.minor.build`
<br>Versions before 1.0.0 though can have small feature additions in +0.0.1 updates.
<br>This can lead to some features not being listed for that version.

Version 1.0.0 will happen when certain important features are implemented.

The content of future updates used to be predetermined, but various circumstances 
resulted in that not really being followed, so it was changed to "whatever I wanna do next".

## Road to 1.0.0 (Required for core)

### 0.1.0: First version

- Options
  - Goals: Ghetsis, Alder, Cynthia, Cobalion, TM/HM hunt, Seven sages, Legendary hunt, Pokémon master
  - Version: Black, White
  - Shuffle Badges: No, shuffle between leaders, leaders can have any "badge", anywhere
  - Shuffle TMs/HMs: Shuffle between NPCs, shuffle HMs to gym leader rewards, NPCs can have any "TMxx" or "HMxx", anywhere
  - Dexsanity (only vanilla encounters)
  - Season control
  - Modify item pool: Useless key items, Useful fillers, Ban bad items
  - Modify Logic: Require Dowsing Machine
  - Reusable TMs
- Rom changes
  - Change roadblocks
  - Make evolution items obtainable somewhere
  - Remove trade and time based evolutions
  - Static encounter, gift, and trade resetting
  - Vanilla items don't get added to the bag
  - Gym leaders setting a custom flag instead of checking for the badge
  - Rage Candy Bar and fossils as key items
- QoL
  - Rom updates
  - Optional re-patch skipping
  - UT map tracker

### 0.2.0: Important backwards-compatibility-breaking changes

- See title

### 0.3.0: Actual randomization

- Options
  - Wild pokémon randomization
    - Also enables full dexsanity
  - Trainer pokémon randomization
  - Adjust levels
  - Encounter Plando
  - Master Ball seller (OptionSet), random cost in range if multiple
    - N's Castle
    - Cheren's mom
    - PC
    - Undella Mansion seller, always offering with a random price
    - Cost: Free
    - Cost: 1000
    - Cost: 3000
    - Cost: 10000
  - All pokémon seen (added in patch)
  - Modify Encounter Rates (added in patch)
  - Experience Multiplier (added in patch)
  - Plugin system (added in patch)
- UT auto-tabbing (added in patch)

### 0.4.0: Advanced Plandosanity

- Modify Levels option
  - Simple method, shown on Webhost
  - Advanced method, more capabilities
- Funny dialogue
  - Funny mode, including actually funny things
  - Efficient mode, making a lot of text shorter
- Text Plando
  - Text extractor setting in patching process
- Dexsanity plando (custom behavior of the Dexsanity option)
- More modifiers
  - Randomize Wild Pokémon
    - Prevent overpowered pokémon
    - Prevent bad early pokemon
  - Randomize Trainer Pokémon 
    - Prevent overpowered pokémon
    - Evolve when possible
    - Force fully evolved
    - Type themed
    - Themed gym trainers
    - Shuffle gym leader types
    - Rivals keep starter
- Randomization Blacklist
  - Wild pokémon
  - Trainer pokémon
- Stats randomization
  - Base stats
  - Evolutions
  - Types
  - Catch rates
  - Levelup movesets
  - TM/HM compatibility
- Stats plando (with all randomizable stats at that time)
- Replace Evolution Methods option
- Combined goals
- An NPC in Accumula Town telling you some information about the world
- Filler Items Blacklist option

### Other stuff required for 1.0.0

- Scripting system (required for many other features)
- arm7 expansion (required for advanced assembly)
- Options
  - More wild pokémon randomization modifiers
    - Dungeon 1 to 1
    - Global 1 to 1
  - More trainer pokémon randomization modifiers
    - Prevent bad early pokemon
    - Rivals take from box
    - N uses pokemon from nearby
    - More or less per trainer
  - Goals: Regional Pokédex, National Pokédex, Custom Pokédex
  - Seensanity (Only accounting for wild pokémon at first, trainer teams later; has impact on All Pokémon Seen)
  - Trainersanity
  - Formsanity (not that many checks)
  - Shinysanity
  - Dexcountsanity
  - Seencountsanity
  - Dexgendersanity
  - Seengendersanity
  - Trainer pokémon plando
  - Decrease trainer eyesight
  - Customize roadblocks
    - Relic castle room filling with sand unlockable via an item
    - Extra cuttable trees
    - Rock Smash rocks
  - Starter/Static/Gift/Trade/Legendary pokémon randomization
  - Seen count checks modifier, e.g. Prof Juniper TM rewards
  - Fan club chairman levels checks modifier
  - Adjust encounters (like Adjust levels, but with species, based on base stats)
  - Disable certain location groups
    - Hidden items
    - Field items (will also disable min_once items)
    - Abyssal Ruins
    - Post goal locations
  - Ingame options (things changeable in PC, moving Experience modifier here)
    - Season control (only when vanilla or changeable, not randomized)
    - Shiny chance modifier (Only activated if Shinysanity not off)
- Dowsing Machine as a hard requirement for hidden items (with option)
- Reducing encounter slots in Modify Encounter Rates
- Trainer rebattling
- Xtransceiver being required to see certain story sequences (with some of them giving items)
  - Also, dynamic Xtransceiver item that automatically adds the correctly gendered version to the game
- Make HMs forgettable
- Expand plugins to client

## Post-1.0.0 stuff

- Options
  - Stats randomization
    - Abilities
    - Gender Ratio (+ limit)
    - Move tutor compatibility
    - Held items
    - Egg groups
    - Pokémon names
  - Move data randomization
    - Move power
    - Move type
    - Move accuracy
    - Move category (only Physical <-> Special)
    - Type effectiveness chart
    - Move names
    - TM/HM content
  - Fairy type
  - Levelup curve modifier
  - Dynamic version
  - Door shuffle
  - Shuffle roadblock requirements
  - Original content
    - Story scenes
    - Community-made trainers + teams
    - Types
    - Berry fields
  - Free fly destination
  - Trainer randomization (i.e. what trainer you're actually battling against)
    - With plando capabilities
  - Trashsanity
  - Boss fight Plando (gym leaders, elite four (first+second run), Alder, N (N's Castle), Ghetsis, Cheren/Bianca (postgame)) (?)
  - Story fight Plando (Cheren, Bianca, N, ...) (?)
  - DeathLink
  - Wonder trade
  - Multiworld gift Pokémon
  - Phenomena activation (vanilla, any badge, Striaton Gym, always)
  - BGM randomization
  - Cutscenes shortening
  - Dusk cloud hunt (dusk clouds have a chance to give a check)
- Offline singleplayer
  - i.e. generating a single world will produce a romhack playable without connecting to a server
- Display other players and item names ingame
- Universal language support
- Traps
- Collected field items removal setting
