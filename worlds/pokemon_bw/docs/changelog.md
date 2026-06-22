# Changelog
Versions are sorted in ascending order, i.e. the most recent changes are at the top.

## 0.4.0

### Content and QoL

- Added `Modify Levels` option (expanded from v0.3.99 pre-release)
  - Simple method (how it will be shown on Webhost):
    - Encounter types: `Trainer`, `Wild`
    - Modes: `Multiply`, `Add`, `Power`
  - Advanced method (cannot be shown on Webhost, but with more capabilities)
    - Same as simple, but accepts multiple chained calculations
- Added a location group for season-dependant item locations
- Added an item group for fossils and another one for TMs and HMs combined
- Reworked how wild encounters are listed in the spoiler log
- Added glitched logic in UT for `Require Dowsing Machine` and `Require Flash` logic modifiers
- Added `Funny Dialog` and `Text Plando` options
  - `funny` and `efficient` choices for `Funny Dialog`
  - Both options require the text plando setting in the host yaml to be enabled
  - Added a setting to enable text extraction upon running a patch file
- Added plando mode to `Dexsanity` option
- Added more modifiers for `Randomize Wild Pokémon`:
  - `Prevent overpowered pokemon`
    - Other modifiers take priority over this, except `Similar base stats`
    - Adjustable threshold (`Overpowered threshold` in `Pokémon Randomization Adjustments`)
  - `Prevent bad early pokemon`
    - Prevents Wonder Guard and fixed HP attacks before Castelia City
- Added more modifiers for `Randomize Trainer Pokémon`:
  - `Prevent overpowered pokemon`
    - Takes priority over most other modifiers, except `Rivals take from box`
    - Adjustable threshold (`Overpowered threshold` in `Pokémon Randomization Adjustments`)
  - `Evolve when possible`
  - `Force fully evolved`
    - Adjustable threshold (`Force evolutions threshold` in `Pokémon Randomization Adjustments`)
  - `Type themed`
  - `Themed gym trainers`
  - `Shuffle gym leader types`
    - Gym leaders now always have vanilla-type themed teams by default
  - `Rivals keep starter`
    - They also always evolve when possible
- Added `Wild Randomization Blacklist` and `Trainer Randomization Blacklist` options
  - The wild blacklist might not prevent some pokémon for various reasons (including other options)
  - Ignored by `Encounter Plando`
- Added more choices to `Modify Encounter Rates`:
  - `One per method`
  - `Dexsanity friendly`
- Added `Randomize Base Stats` option with the following modifiers:
  - `Randomize`
  - `Random total`
  - `Follow evolutions`
- Added `Randomize Evolutions` option with the following modifiers:
  - `Randomize`
  - `Random methods`
  - `Common type`
  - `Follow type`
  - `Multiple pre-evolutions`
  - `More or less branches`
  - `Looping evolution lines`
  - `Every level`
  - `Pair stats`
  - `Pair 50 50`
  - `Increasing stats`
- Added `Randomize Catch Rates` option with the following modifiers:
  - `Shuffle`
  - `Randomize`
  - `Follow evolutions`
  - `Correlate with base stats`
- Added `Randomize Level Up Movesets` option with the following modifiers:
  - `Randomize`
  - `Keep types`
  - `Progressive power`
  - `Keep amount`
  - `Keep levels`
  - `Follow evolutions`
  - `Start with 4`
- Added `Stats Randomization Adjustments` option, currently with the following parameters:
  - `Stats total minimum`
  - `Stats total maximum`
  - `Level up evo weight`
  - `Maximum evo level`
  - `Catch rates minimum`
  - `Catch rates maximum`
  - `Levelup moves amount minimum`
  - `Levelup moves amount maximum`
- Added `Stats Plando` option, currently with the following keys for every species:
  - `base_hp`
  - `base_attack`
  - `base_defense`
  - `base_sp_attack`
  - `base_sp_defense`
  - `base_speed`
  - `catch_rates`
  - `evolutions`
  - `override_evolutions`
  - `levelup_moveset`
  - `override_levelup_moveset`
- Added `Replace Evolution Methods` option with the following modifiers:
  - `Locations`
  - `Friendship`
  - `PID`
  - `Stats`
- Added what shall not be said at times
- Added a few (new and returning) locations:
  - `Nuvema Town - Item #2 from Mom`
  - `P2 Laboratory - Item from scientist #1` (and `#2`)
  - `Castelia City - Item from harlequin in Studio Castelia` (now requesting a fixed type)
  - `Royal Unova - Item for defeating every trainer` (now time independent)
  - `Driftveil City - Item from lady asking for a pokémon knowing a certain TM move` (now requesting a fixed TM move)
  - `Lacunosa Town - Item from girl for showing a Shaymin`
  - `Village Bridge - Item from fisherman for showing a certain pokémon caught today #1` (+ `#2`, `#3`, `#4`, and `#5`) (now requesting a fixed pokémon)
- Added combined goals
- Added `Filler Items Blacklist` option

### Bug fixes and technical stuff

- Changed some locations' names
- Added a missing hidden item location in Chargestone Cave B2F
- Fixed "Striaton City - TM from Fennel" not being able to contain an HM with certain options
- Reduced frequency of different forms of the same pokémon in randomization
- Wrote down levelup moveset data
- Fixed small error with encounter plando
- Tweaked many option descriptions
- Made wild randomization not having to ensure 115 different obtainable pokémon if `All Pokémon Seen` is enabled
- Made the Gracidea also accept non-event Shaymins
- Fixed logic of move evolutions
- Wrote down move IDs

### Is this version compatible with older multiworld slots and save files?
No

## 0.3.34

- Fixed client crashes resulting from the recently added funny dialog
- Fixed small bugs of the recently added funny dialog
- Tweaked the Chargestone Cave chuckster throwing animation
- Fixed the new NPC in Accumula Town not appearing

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9)
However, tracking worlds generated before 0.3.27 might show incorrect Dexsanity logic in UT

## 0.3.33

- Fixed multiple changes to the base ROM being reverted in previous updates
- Made the Plasma grunts in Chargestone Cave always stay in the cave
  - This fixes them potentially never appearing when playing through Chargestone Cave in reverse
- Added an NPC to the southern entrance of Chargestone Cave that throws you to the northern exit
  - He only appears after defeating N in Chargestone Cave
- Removed the forced Musical Theater dress up minigame
- Fixed the fight with N in Nacrene City being missable when doing the Pinwheel Forest events before that
- Added a bit of funny dialog at the start of the game
- Added an NPC next to the Pokémon Center in Accumula Town, who will be used for a feature in 0.4.0

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9)
However, tracking worlds generated before 0.3.27 might show incorrect Dexsanity logic in UT

## 0.3.32

- Fixed multiple plugins nullifying each other's modifications to the ROM
- Fixed modifications by plugins to arm7 not being written to the ROM

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9)
However, tracking worlds generated before 0.3.27 might show incorrect Dexsanity logic in UT

## 0.3.31

- Reworked plugins system and added capabilities to modify world generation
  - Adding the hooks `generate_early`, `generate_encounters`, `create_regions`, `create_items`, `write_patch`
  - However, this breaks old plugins
- Slightly changed the `Reusable TMs` choice `yes` to `yes_please`
  - Old yamls will still work and quietly fix the name change
- Added an lz11 decompress algorithm
- Fixed the Master Ball seller in N's Castle

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9)
However, tracking worlds generated before 0.3.27 might show incorrect Dexsanity logic in UT

## 0.3.30

- Added a button to abort patching if any patching plugin failed
- Added support for the "Show dexsanity on wild encounters" feature of the Poptracker pack
- Made the client uncheck legendary pokémon in the Poptracker pack if reset by defeating Ghetsis/Alder
- Changed the UT map integration to using the (external) Poptracker pack instead (@Radis7Noir)
  - This removes the need for the apworld with maps
- Added the `plugin_options` option
- Put slot data (partially) into the patch file

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9)
However, tracking worlds generated before 0.3.27 might show incorrect Dexsanity logic in UT

## 0.3.29

- Added the patching plugin system

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9)
However, tracking worlds generated before 0.3.27 might show incorrect Dexsanity logic in UT

## 0.3.28

- Fixed generation failures resulting from the last update

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9)
However, tracking worlds generated before 0.3.27 might show incorrect Dexsanity logic in UT

## 0.3.27

- Fixed `Experience Multiplier` not automatically being set to the value specified in the yaml
- Fixed `All Pokémon Seen` not being applied to the save file
- Tried fixing a rare bug regarding the PopTracker pack and data storage
- Removed `any_badge`/`any_tm_hm` from `Shuffle Badge Rewards`/`Shuffle TM Rewards`
  - Old yamls with these choices will instead interpret them as `shuffled`
- Removed `Prioritize key item locations` from `Modify Logic`
  - Old yamls with this modifier will just ignore it

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9)
However, tracking worlds generated before 0.3.27 might show incorrect Dexsanity logic in UT

## 0.3.26

- Removed HMs being forgettable due to game breaking bugs resulting from it

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9).
However, tracking worlds generated before 0.3.25 might show incorrect Dexsanity logic in UT

## 0.3.25

- Fixed incorrect logic for getting access to the roamer
- Fixed unit test failures on GitHub due to the `ndspy` library missing (next try)
- Tweaked the option description for the `Stats leniency` parameter
- Fixed the seen count locations not accounting for the `All Pokémon Seen` option
- Made HM moves forgettable without the move deleter
- Tweaked the `dump_patched_files` part of the patching process

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9).
However, tracking worlds generated before 0.3.25 might show incorrect Dexsanity logic in UT

## 0.3.24

- Tweaked `Prevent rare encounters` to prevent accidentally merging everything to a single species
- Fixed the current season (if randomized) always being set to the starting season upon reconnecting

### Is this version compatible with older multiworld slots and save files?
Yes, back to 0.3.0, except the pre-release 0.3.99(9).
However, tracking worlds generated before 0.3.24 might show incorrect Dexsanity logic in UT

## 0.3.23

- Fixed hidden items (that are recurring in vanilla) not being checked
- Fixed crashes in the Pokédex due to missing flags for alternate forms
- Added `enable_arm7_expansion_test` setting

## 0.3.22

- Fixed backwards compatibility issues due to the new options from 0.3.21

## 0.3.21: "I'm going to make palex and Radis unemployed" update

- Added `Experience Multiplier` option
  - Also added a menu to the PC in Pokémon Centers to adjust it ingame
- Added `All Pokémon Seen` option
- Fixed compatibility issues with AP 0.6.7 release candidates
- Fixed player names with too many non-Ascii characters leading to a corrupted rom
- Tweaked the menu structure of the PC in Pokémon Centers
- Fixed backwards compatibility issues with old yamls
- Tweaked option descriptions to make them a bit more Options Creator-friendly
- Reworked `any_badge` and `any_tm_hm` once again

## 0.3.20: "The Pokédex is actually a tracker" update

- Fixed the Pokédex seen count not being sent completely to Poptracker
- Fixed unit test failures on GitHub due to the `ndspy` library missing
- Fixed adding an Encounter Plando on a nonexistent slot leading to an error
- Disabled Johto-exclusive balls from being shuffled into the itempool, as they're unusable ingame
  - You can still send them via server commands though
- Changed the trades bitmap for Poptracker to indicate the first time talking to the NPC instead of a finished trade
- Actually fixed the sandwich minigame on Village Bridge not being repeatable on the same day
- Fixed the Pokédex areas keeping the vanilla locations even if wild encounters are randomized or plando'd
- Fixed the Master Ball seller in N's Castle soft locking the game

## 0.3.19: DIG. IS. FINALLY. USABLE. update

- Features/QoL:
  - Added support for unweighted/weighted lists, `random`, and `random-range-x-y` to `Pokemon Randomization Adjustments`
  - Made the Pokémon Fan Club chairman also give the 25+ levels check if shown a pokémon with 50+ levels growth
    - Also made the (not modified) 99 levels reward give both the 25+ levels and 50+ levels checks
  - Made Running Shoes being enabled right from the start
    - This is only temporary, as the Running Shoes will be added as an AP item in a later update
  - Made some in-game text related to roadblock items more accessible to new players
    - Also added extra dialog for the Dreamyard traffic cone
  - Removed the once-per-day limitation of the massage lady in Castelia City

- Fixes:
  - Fixed using Dig outside of battles (with `season_control` being set to any other than `vanilla`) crashing the game
  - Fixed `any_badge` and `any_tm_hm` choices potentially removing incorrect Item instances form the multiworld itempool
  - Fixed `any_badge` and `any_tm_hm` choices ignoring local items of other players
  - Fixed adding `Consider trades` to `Modify Logic` occasionally leading to generation failures
  - Fixed `Route 6 - Item from scientist for all Deerling forms` not having the extended hint if `Dexsanity` is set to 0
  - Fixed extended hints being inconsistent with evolutions and trades
  - Fixed `Nacrene City - Item from waitress in Café Warehouse` also giving the vanilla item
  - Fixed the Aha quiz price locations sometimes being swapped and sometimes also giving the vanilla item
  - Fixed sage Ryoku being invisible in Relic Castle B1F castleside if entered before the events in Dragonspiral Tower
  - Fixed hidden items (that are normally reappearing) being detected by the Dowsing Machine again immediately
    - However, they will still reappear after some time, which won't be fixed in the foreseeable future
  - Fixed the evolution items seller in Shopping Mall Nine ending abruptly after selecting "Cancel"

- Other stuff:
  - Made `Consider trades` require either `Consider evolutions` or wild pokémon being randomized
  - Renamed `CasefoldOptionSet` to `ToggleSet` and added QoL stuff to it on the development side
  - Renamed multiple modifiers of some OptionSet options (do note that old yamls do **not** break)
  - Raised minimum required AP version to 0.6.4
  - Added bitmaps of statics and trades for Poptracker

## 0.3.18: "But I did beat Cynthia..." update

- Features:
  - Added "Post-Ghetsis locations" group
  - Made `Randomize Wild Pokemon` (and similar options) automatically add `Randomize` if any other modifier is added
  - Added `Rare encounters threshold` key to `Pokémon Randomization Adjustments`, intended for the `Prevent rare encounters` modifier
    - Also changed the default to 8, in order to prevent conflicts with the `Modify Encounter Rates` option
  - Added an extended location hint for `Route 6 - Item from scientist for all Deerling forms`
  - Added `Consider evolutions/static pokemon/trades/form change` to `Modify Logic`
  - Added places of pre-evolutions and trade requests to extended hint information of Dexsanity checks

- Fixes:
  - Fixed the flag for beating Cynthia not being correctly sent to Poptracker
  - Fixed multiple Dexsanity checks being rolled when not possible (or vice versa)
    - This includes Pansage sometimes not having a check even if `Ensure all obtainable` is included
  - Fixed `Pokémon Randomization Adjustments` crashing when given an empty dictionary
  - Fixed Marvelous Bridge being forgotten by the `Adjust levels` option
  - Fixed incorrect entrance logic of Moor of Icirrus

- Other stuff:
  - Improved filler item generation performance
  - Tweaked option descriptions to make them friendlier towards new players
  - Made `Icirrus City - Item from Pokémon Fan Club chairman for gaining 50 levels` logically require access to Ghetsis
  - Added static and trade encounters to slot data for Poptracker
  - Added patch version range accepting
  - Tweaked error messages for incompatible base ROMs in the patching process
  - Added the requirement to reach Shopping Mall Nine for stats based evolutions
  - Removed `Prevent rare encounters` being forbidden with certain `Modify Encounter Rates` values
    - Instead, an OptionError is now raised when a combination of options leads to not having enough wild 
      randomization slots for all guaranteed encounters
  - Added `revert()` and `stack()` to `version.py`
  - Made the Prof. Juniper Pokédex seen count locations check the national Pokédex instead of the regional one
    - Also adjusted the apworld's logic to reflect that

## 0.3.17

- Fixed encounter plando failing with certain randomization modifiers
- Fixed Trial Chamber logic not accounting for the strength boulder
- Fixed possible softlocks due to level up + move evolutions not accounting for access to the move reminder
- Removed the Heart Scale requirement for the move reminder

## 0.3.16

- Fixed template yamls not working/being rejected

## 0.3.15

- Fixed custom and randomized encounter rate modification not working
- Actually fixed Trial Chamber logic
- Fixed encounter plando not working without randomized wild encounters

## 0.3.14

- Added `Modify Encounter Rates` option
- Added support for the Poptracker pack
- Made reaching Nacrene City a logical requirement for friendship evolutions
- Added form changes for Deerling, Sawsbuck, Rotom, and Deoxys to logic
- Tweaked the `Adjust Levels` option for some earlier postgame maps

- Fixed manifest missing the container version fields
- Fixed unit test failures due to `Shuffle Badge Rewards` and `Shuffle TM Rewards` shenanigans
- Fixed badge and TM/HM locations not being excludable or prioritizable
- Fixed the Deerling forms location once again
- Fixed logic of Trial Chamber (including the static Terrakion)
- Fixed nondeterministic Dexsanity location creation
- Fixed generation failures for certain combinations of Encounter Plando and randomization modifiers
- Fixed small miscalculations with `Prevent rare encounters` in wild pokémon randomization
- Fixed Sneasel not being able to evolve
- Fixed rom not being automatically updated when it should
- Fixed incorrect level adjustments
- Fixed sage Zinzolin appearing twice in Cold Storage under certain circumstances
- Fixed potentially not having 115 Unovan pokémon available when randomized
- Fixed weird text box behavior of PC Master Ball seller
- Removed different Arceus forms
  - Also fixes a possible softlock due to Challenger's Rock

## 0.3.13

- Made sure there is always at least one fighting type pokémon obtainable (for the challenge rock)
- Fixed the sandwich minigame on Village Bridge not being repeatable on the same day
- Fixed beating Ghetsis again triggering post-Alder stuff
- (Hopefully) fixed not being able to enter the Pokémon League after beating Ghetsis
- Added setting for dumping patched files (for debug purposes)

## 0.3.12

- Fixed the Wingull grams reward location not working
- Added an error message for too old AP versions

## 0.3.11

- Added version without UT submaps to release
- Fixed `Mistralton Cave 3F` locations not appearing on the overworld map in UT
- Fixed logic of Pinwheel Forest's east side
- Fixed logic of `Route 8 - Item from Bianca` (this got incorrect logic as a side effect of the previous fix)

## 0.3.10

- Added many more maps and auto-tabbing (@palex00, @Radis7Noir, @Darvitz, darkfire006)
- Fixed `Moor of Icirrus - Hidden item behind boulder` having incorrect logic

## 0.3.9

- Added a location group for items in Abyssal Ruins
- Added the `Start Inventory From Pool` option
- Fixed season-dependant locations not being excluded when wild pokémon are randomized
- Fixed Wellspring Cave B1F not being considered in `Require Flash` logic modifier (@Seatori)
- Fixed some gym leaders not being present in their gyms in some situations
- Fixed sage Zinzolin not appearing in Cold Storage again if first scene was played after Ghetsis
- Fixed Bianca on route 8 only triggering when standing in front of the bridge gate
- Fixed the Wingull on route 13 giving the item even without having all grams

## 0.3.8

- Fixed Master Ball sellers not working if the multiworld was generated before 0.3.4

## 0.3.7

- Fixed UT crashing when updating past 0.3.3

## 0.3.999 (pre-release)

- Fixed `Modify Levels` option not capping levels at 100
- Fixed `Modify Levels` crashing when certain keys are not provided in the yaml

## 0.3.99 (pre-release)

- Added `Modify Levels` option
  - Modes: `Multiply`, `Add`, `Power`
  - Encounter types: Trainer, Wild

## 0.3.6

- Added evolutions to extended Dexsanity hints
- Fixed "... for seeing x Pokémon" locations to only account for Unovan Pokémon
  - Also made sure there are always enough species obtainable for them when randomized
- Fixed Encounter Plando overwriting the slots multiple times, leading to logic errors
  - Multiple entries overwriting the same slot(s) now displays a warning in world generation
- Fixed `Route 6 - Item from scientist for all Deerling forms` sometimes being impossible 
  due to not all Deerling forms being obtainable
- Fixed the logic of item-based evolutions

## 0.3.5

- Fixed including any Dexsanity location crashing world generation
- Made automatic rom updating also downgrade newer roms (due to possible conflicts with used flags etc.)
- Added apworld manifest

## 0.3.4

- Fixed some randomized trainer Pokémon still having the vanilla Pokémon's moves
- Fixed randomized seasons not being written into save data properly, leading to all seasons being available immediately
- Fixed enabling multiple Master Ball sellers leading to not all of them being available
- Made flag and item writing in client more error-proof
- Fixed `Nacrene City - Item from Lenora after Relic Castle` not showing up in UT
- Added extended hint information for Dexsanity locations
- Added location aliases for both Nidorans' Dexsanity locations in UT
- Fixed Aha prizes having flipped flags
- Added `Require Flash` to the `modify_logic` option
- Fixed UT crashing when Encounter Plando was used in generating
- Some QoL changes for writing the player yaml:
  - Made all OptionSet options ignore casing
  - Made Encounter Plando ignore casing for argument names, seasons, and methods
  - Made Encounter Plando accept `season` and `slot` as alternatives to `seasons` and `slots`
- Tweaked the Master Ball Seller option:
  - Removed `:` and `'` characters from modifiers
    - However, old yamls are still compatible
  - Added the possibility to add any cost modifier in range of 0 to 30000
  - Removed throwing an option error if any seller, but no cost is added
    - No cost modifier now instead defaults to 3000
- Added error message for patch file being too old
- Added automatic ROM updates
- Added details for incorrect ROM header error while patching
- Fixed the Musharna static encounter not appearing immediately
- Made the Undella Town Mansion seller snap his prices to 500-steps
- Changed the dialog of the grunts on route 8 to better reflect how to make them disappear
- Fixed the evolution items seller in Shopping Mall Nine giving a `???` item when pressing B
- Added a warning to UT users when tracking with a not entirely compatible apworld version (e.g. due to RNG changes)
- Added `None` species to Encounter Plando to make a plando entry not put anything into the specified slot(s)

## 0.3.3

This update only ports over the fixes from the 0.2.2 update, which was released right before this:
- Fixed fossils not being revivable after the Plasma grunts stole the Dragon Skull
- Fixed Professor Juniper ignoring the national dex for her TM rewards
- Fixed Professor Juniper not always being in the lab
- Fixed Champion goal triggering after fighting Ghetsis

## 0.3.2

- Made option descriptions in template yamls look nicer
- Added some more information to the option description of `master_ball_seller`
- Fixed certain wild Pokémon randomization modifiers leading to nondeterministic randomization
  - This also fixes UT having wrong logic (especially regarding Dexsanity), but already generated worlds cannot be fixed
  - Has to be tested using UT
- Fixed client crashing immediately if Master Ball seller cost is set to anything other than 0 or nothing
- Fixed multiple custom menus in the Pokémon Center PC freezing the game after displaying a text box

## 0.3.1

- Fixed UT not working

## 0.3.0: Actual Randomization

### Content

- Added wild pokémon randomization, including the following modifiers:
  - Randomize
  - Ensure all obtainable
  - Similar base stats
  - Type themed areas
  - Area 1-to-1
  - Merge Phenomenons
  - Prevent rare encounters
- Added a master ball seller option
  - 4 different sellers: NPC in N's Castle, Undella Mansion seller, PC, Cheren's Mom (multiple choice)
  - Different cost modifiers: Free, 1000, 3000, 10000 (multiple choice, random cost in range if multiple)
- Added level adjusting option for wild and trainer Pokémon
- Added trainer pokémon randomization, for now including following modifiers:
  - Randomize
  - Similar base stats
- Added encounter plando, currently only for wild pokémon
  - Working with and without randomized wild pokémon

### QoL

- Made key items and other important items get checked and re-added if not in save file after connecting
- Wrote player name into rom, hopefully making the client always automatically connect to the correct slot
- Changed the item description of a few non-vanilla key items
- An option to adjust certain aspects of Pokémon randomization
  - Only having the leniency for "Similar base stats" modifiers for now

### Bug fixes

- Fixed rare(?) BizHawk client crashing due to slotdata not being received yet
- Fixed items getting lost after soft resetting after receiving an item after the last save
- Fixed TM/HM checking NPC not showing up when `pokemon_master` is chosen as the goal

## 0.2.3

- Fixed certain AP-only NPCs not showing up in save files that were affected by a bug from before 0.2.2

## 0.2.2

This update was published after 0.3.2, thereby including a few retroactive bug fixes and QoL things:
- Fixed rare(?) BizHawk client crashing due to slotdata not being received yet
- Fixed items getting lost after soft resetting after receiving an item after the last save
- Made key items and other important items get checked and re-added if not in save file after connecting
- Fixed TM/HM checking NPC not showing up when pokemon_master is chosen as the goal
- Changed the item description of a few non-vanilla key items

New fixes:
- Fixed fossils not being revivable after the Plasma grunts stole the Dragon Skull
- Fixed Professor Juniper ignoring the national dex for her TM rewards
- Fixed Professor Juniper not always being in the lab
- Fixed Champion goal triggering after fighting Ghetsis

## 0.2.1

- Fixed UT not working
- Fixed generation failures when having different `shuffle_badges` values in the same multiworld

## 0.2.0: Important backwards-compatibility-breaking changes

- Fixed one of the hidden items on route 18 having weird behavior
- Fixed Legendary Hunt and Pokémon Master reporting goal completion upon defeating Cynthia
- Fixed problems with opening the client without using the patch file by restructuring slot data and datapackage to be read from network
- Fixed Darmanitan statues not working because of the Rage Candy Bar being placed into the wrong bag
- Fixed events in Nacrene City after Relic Castle not triggering properly
- Fixed location names of two hidden items in Challenger's Cave
- Reclassified TMs/HMs as `progression_deprioritized` opposed to just `progression` if needed for goal
- Made Aha's quiz in Icirrus City trigger whenever the player enters the building
- Disabled checks for time- and RNG-dependant locations
- Added some item and location groups
- Disabled dexsanity checking in client if there are no dexsanity checks
- Actually implemented UT being able to generate without a yaml
- Fixed debug menu option namings and added print flag command
- Added TM/HM bag sorting option to PCs
- Added region-based logic to level-dependant evolutions
- Allowed HMs to be placed into TM NPC locations without the risk of a softlock
- Optimized encounter event creation to reduce playthrough calculation time
- Added `Prioritize key item locations` to `modify_logic`
- Reduced FillError rate for worlds with `shuffle_badges`/`shuffle_tm_hm` set to `any_badge`/`any_tm_hm` 
- Made defeating Ghetsis trigger right after winning the battle

## 0.1.7: This was supposed to only be bug fixes...

- Fixed bizhawk client not checking for correct rom header, leading to problems with running other roms
- Fixed the harlequin in Studio Castelia not being excluded even though the wanted type changes daily
- Fixed repeatable checks to either triggering only once or giving vanilla items afterwards
- Added remaining forms without individual stats
- Added back the requirement to provide a yaml for UT
- Fixed bag placement of all ev wing items and Casteliacone
- Fixed reward for Royal Unova not being excluded
  - The Royal Unova is only accessible at certain day times
- Fixed Slowpoke's evolution's priority
- Fixed Dreamyard's gift encounter adding all 3 options to logic even though you could only get a specific one
- Fixed machine part npc on route 4 always letting the player pass
  - Also fixed his weird behavior
- Fixed Chargestone Cave being invisibly blocked when fighting Clay after getting rid of the webs
- Fixed gym TM rewards not containing TMs/HMs when TMs/HMs are shuffled
- Added `modify_logic` option, currently only including `Require Dowsing Machine`
- Added 3 new goals:
  - `Cobalion`: Defeat or catch Cobalion
  - `Legendary hunt`: Defeat or catch all legendary encounters, including Volcarona
  - `Pokémon master`: Complete all other goals

## 0.1.6: UT Map update

- Added map tracker for Universal Tracker (by @palex00)
- Fixed logic of `Route 6 - TM from Clay`
- Fixed logic of phenomenon encounters
- Fixed daily treasure NPC on route 13 giving a non-AP item immediately
  - The intended behavior is to give an AP item first and then the following days a random vanilla item
- Fixed the infielder on route 9 instantly throwing the item at you even when entering from Opelucid City

## 0.1.5: Bringing Back Badge Requirements for HMs update

- Fixed sage Gorm being invisible but still triggering before Ghetsis
- Fixed Time Capsule and Liberty Pass not being recognized
- Fixed doing the Pinwheel Forest events before beating Lenora leading to a softlock
- Added option `hm_with_badge` to `shuffle_tm_hm`

## 0.1.4

- Fixed bad indirect connections registering
- Restructured evolution events to allow party member evolutions
- Added simple unittests
- Fixed not patching certain parts of the rom
- Fixed hidden items not being collectible

## 0.1.3: Ghetsis' Softlock Order update

- Fixed checking locations crashing the game
- Fixed the parcel man in Striaton City not recognizing the parcel
- Fixed Striaton City gym not being patched properly
  - This fixes multiple bugs happening in Striaton City
- Fixed man in black in Castelia City's Narrow Street not sending the checks if not talked directly to him
- Fixed worker at Twist Mountain entrance asking for **not** having the Jet Badge
- Fixed multiple occasions of comments in script source codes leading to a broken compilation of scripts
- Removed Town Map from item pool since it's always obtained from mom due to a broken script

## 0.1.2: Parcel on Twist Mountain update

- Another Python 3.11 fix
- Fixed a lambda in a for-loop leading to overall faulty logic
- Removed `é` letters from option descriptions
- Merged season patches since they are the same anyway
- Added fossil encounters, making a few more Dexsanity checks possible
- Fixed Abyssal Ruins logic errors
- Fixed setting `season_control` to anything other than vanilla crashing the game instantly
- Fixed logic error with evolutions not requiring their base forms
- Fixed the shift in sent Dexsanity locations
- Fixed hidden items not sending checks and being "collectable" repeatedly
- Fixed the item in Plasma hideout in Castelia City being sent immediately
- Fixed the girl on route 1 giving the vanilla item
  - Also hopefully fixed the guy in southeastern corner of Striaton City giving the vanilla item, but has to be tested
- Fixed logic issues with the location requiring all Deerling forms
- Reworked the repatch-prevention to instead look for the existence of an already patched rom
  - i.e. the patching process will only happen again if the already existing patched rom has been deleted

## 0.1.1: Day One Patch™ update

- Fixed items not being received at all
- Fixed Dexsanity always leading to generation failures
- Fixed Python 3.11 crashing due to not yet used options
- Packed `ndspy` into the apworld for now because of AppImage problems
- Fixed Shelmet's evolutions leading to generation failures

## 0.1.0: First release

### Rom

#### Gameplay
- Changed some roadblocks
  - Man hindering the player from entering route 3 now requires the parcel
  - Traffic cone in Dreamyard blocking the basement now vanishes when coming close to it with the basement key
  - The grunts blocking the entrance to Pinwheel Forest now look for the loot sack
  - A shadow triad member now blocks you from leaving Pinwheel Forest without the dragon skull
  - The worker in the middle of route 4 is now looking for the machine part
  - The worker blocking you from going to B2F and below in Relic Castle now requires the explorer kit
  - The workers blocking Marvelous Bridge now let you pass with a blue card
    - They were also moved a little bit to prevent one-way passing from the other side
  - Entering Driftveil Drawbridge now requires a tidal bell, even coming from Driftveil City
  - The spider web blocking Chargestone Cave was multiplied and moved a bit south to prevent one-way passing
    - The script was also slightly altered to check for the quake badge instead of having Clay defeated
  - The worker blocking Twist Mountain was moved a bit to prevent one-way passing
    - The script was also slightly altered to check for the jet badge instead of having Skyla defeated
  - The grunts blocking Tubeline Bridge now disappear when seeing the light or dark stone
    - They were also moved a little bit to prevent one-way passing from the other side
  - The black belt blocking Challenger's Cave now vanishes when receiving the red chain
  - The police officer blocking the gate between Opelucid City and route 11 now requires Oak's letter to pass
- Made evolution items available to purchase or receive multiple times
  - Fire, water, and leaf stone in Castelia City
  - Thunder stone and metal coat in Chargestone Cave
  - Moon and sun stone in Twist Mountain
  - Dusk, dawn, and shiny stone on route 10
  - King's rock, protector, dragon scale, reaper cloth, and oval stone in Shopping Mall Nine
  - Electirizer, magmarizer, upgrade, dubious disc, prism scale, deep sea tooth, and deep sea scale in Undella Town
  - Razor fang and razor claw in Giant Chasm (as recurring hidden item on a suspicious rock)
- Changed trade and time based evolutions
  - Kadabra to Alakazam at level 32
  - Machoke to Machamp at level 40
  - Graveler to Golem, Haunter to Gengar, Boldore to Gigalith, and Gurdurr to Conceldurr at level 37
  - Karrablast to Escavalier and Shelmet to Accelgor at level up with the other one or its evolution in your team
  - Eevee to Espeon/Umbreon using a sun/moon stone
  - Poliwhirl to Politoed and Slowpoke to Slowking at level up while holding a king's rock
  - Onix to Steelix and Scyther to Scixor at level up while holding a metal coat
  - Rhydon to Rhyperior at level up while holding a protector
  - Seadra to kingdra at level up while holding a dragon scale
  - Electabuzz to Electivier at level up while holding an electirizer
  - Magmar to Magmortar at level up while holding a magmarizer
  - Porygon to Porygon2 at level up while holding an upgrade
  - Porygon2 to Porygon-Z at level up while holding a dubious disc
  - Feebas to Milotic at level up while holding a prism scale (also removed the contest based evolution)
  - Dusclops to Dusknoir at level up while holding a reaper cloth
  - Clamperl to Huntail/Gorebyss at level up while holding a deep sea tooth/scale
  - Gligar to Gliscor at level up while holding a razor fang (at any time)
  - Sneasel to Weavile at level up while holding a razor claw (at any time)
  - Happiny to Chansey at level up while an oval stone (at any time)
  - Budew to Roselia, Chingling to Chimeco, and Riolu to Lucario at level up with high friendship (at any time)
- Added an NPC to Nimbasa City that can change the weather (if `Season Control` is not `vanilla`)
- Added an NPC to Castelia City that checks for the completion of the TM/HM hunt goal
- Added an NPC to Accumula Town that resets static encounters (including gift and trade encounters)
- Made certain events requiring a specific pokémon in your party accept any pokémon of that species
  - Obtaining Zorua / Zoroark using any Celebi / Entei, Raikou, and Suicune
  - Receiving an item in Lacunosa Town / P2 Laboratory for showing any Shaymin / Genesect
- Made certain time based events available all the time
  - The Musharna at Dreamyard now appears every day instead of only on Friday
  - The Munchlax trade in Undella Town is now available during all seasons
  - Time based items in Lacunosa Town and Café Warehouse are now obtainable all the time
- Prevented gym events from being disabled when beating the gym leader
- The grunt at Pokémon League teleporting you to N's castle now stays even after defeating Ghetsis
  - This also makes the fights against N and Ghetsis repeatable

#### Technicalities
- Removed some ItemSub commands (to not lose key items)
- Changed most HasBadge and AddBadge commands to checking and setting a custom flag
- Changed certain items' data
  - Unused key items, the Rage Candy Bar, and fossils are now permanently in your bag
- Added badges, seasons, and "AP Item" as virtual items, i.e. you can collect them, but they won't go into your bag
- Changed all overworld, hidden, and npc items to give "AP Item" instead of their vanilla items
- Added a debug menu to the PC help menu

### APWorld

- Data
  - Data definitions
  - Items
    - Bag items: Berries, key items, main items, medicine, TMs/HMs
    - Badges
    - Seasons
    - DictViews
  - Locations
    - Encounters: Wild, static, gift, trade, legendary, regions + connections
    - Overworld regions + connections
    - Ingame items: Overworld, hidden, npc, badge, TM/HM
    - Dexsanity
    - Methods/Rules: Progress type, access rule, inclusion rules
    - Partial Trainersanity, unused
  - Pokémon
    - Species: Dex number, form, base stats, abilities, evolutions, TM/HM movesets
    - Pokédex lookup
    - Evolution methods
- Docs
  - Changelog (initial)
  - Credits
  - Roadmap (initial)
  - Game info page (partially)
  - Setup page
- Generator
  - Events: Wild/Static encounters, evolutions, goals
  - Items: Badges, key items, min once main items, seasons, TM/HM
  - Locations: Overworld items, hidden items, npc items, badge rewards, TM/HM rewards, dexsanity
  - Manual item placement: Badge rewards, TM/HM rewards
- Patch
  - Procedures: Base patch, slot data, season patch
  - Patch files: Base patches zip, season patches
  - OTPP algorithm
- World class skeleton
- Client
  - Generic BizHawk client
  - Item receiving
  - Flag location checking
  - Dex flags checking
  - Goal checking
  - Slot data file retrieving
- Item handling
  - All item-related things mentioned above
  - Lookup table
  - Random filler items
- Locations handling
  - All location-related things mentioned above
  - Lookup table
- Rom handling
  - Patch file generation
  - Patch file importing
- Options
  - Goal: Ghetsis, Champion, Cynthia, TM/HM hunt, Seven Sages hunt
  - Version: Black, White
  - Shuffle badge rewards: Vanilla, Shuffle, Any "Badge", Anywhere
  - Shuffle TM/HM rewards: Shuffle, Any "TM"/"HM", Anywhere
  - Dexsanity (partially)
  - Season control: Vanilla, Changeable, Randomized
  - Modify item pool: Useless key items, useful filler, ban bad filler
  - Reusable TMs: On, yes, of course, I'm not a masochist
