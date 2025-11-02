# Important stuff

- unown and burmy dexsanity not checking?
- goal option description tm hm hunt
- not being able to go into pokemon league after beating ghetsis
- baker on village bridge not repeatable
- defeating ghetsis again triggers champion goal

# 0.4.0

## APWorld

- More modifiers
  - Randomize Trainer Pokémon 
    - Prevent overpowered pokémon
      - Base stat total threshold adjustable
      - Takes priority over similar base stats
    - Evolve when possible
    - Force fully evolved 
      - Level threshold adjustable
    - Type themed
    - Themed gym trainers (also make gym leaders and elite 4 always have themed teams)
    - Prevent early Wonder Guard and fixed HP attacks
    - Rivals keep first pokemon
    - Rivals take from box
  - Adjust Levels
    - Trainer team (weaker pokémon used in postgame area battles for similar base stats)
- Randomization Blacklist
  - Wild pokémon
    - Will still put every species that is required to be randomized and base stage into at least one slot
    - Ignored by Encounter Plando
  - Trainer pokémon
- extended location hint for deerlings location and challenge rock
- add info when wrong language detected in bizhawk_client
- reword randomization adjustments option description
- add info when choosing the wrong language in patching
- rework regions + events NOW because spheres are weird without them
- account for levels of moves needed for evolving (ancient power, ...)

## Rom

- fast travel npc in chargestone cave from south to north if battled N at north exit
- maybe juniper seen count locations can check for national seen? look at cedric in mistralton city and both other dex seen locations
- make mom stop the player at the door and say funny things for certain reusable tm choices
- skip musical tutorial, because some players have problems
- disable dig outside of battle when season patch included, as a temporary bandaid fix
- desert resort south hidden item not checkable?
- make item names in custom roadblock dialogues a distinguishable color
- fix nacrene city sequence break (though is it actually broken?)
- fix reappearing hidden items still getting detected by dowsing machine because of original flags not being checked
- opelucid city fly flag only set after ghetsis scene?
- make massage lady in castelia repeatable

## Both

- add now-possible locations
- a way to check whether map or fly menu is opened, used for switching to ow map in UT
- Running shoes as an item, making mom cutscene on route 2 a check
- maybe [redacted] is actually possible? but definitely with restrictions
- Dowsing Machine as a hard requirement for hidden items
- one case of goal not triggering reported in sync
- master ball seller not showing up again?
- bgm randomization
- Early game cutscenes shortening option (skipping entire parts in script)
- after everything else: check docs for up-to-date information, update tests, update location names in ut                             

# Not urgent

- dig with seasons patch crashes the game, not fixable?
- look through scripts and remove space checking for specific items
- fill evo method ids
- more inclusion rules
- complete levelup movesets
- advertise on ds romhacking servers
- post MonochromeScriptAssembler to ds romhacking servers
- make simple script compiler, use for starting season, season npc vanish, tmhm hunt npc vanish, and other future stuff
- change rules dict to being filled on the way
- organize imports for type hints behind TYPE_CHECKING
- pitch webhost and template yaml notes, both individual, but template copying from webhost by default
- Fix locations in pokédex if something written to encounter tables
- BizHawk 2.11 having issues with modded gen 5 roms
- rename slot methods to cave/dust cloud/etc everywhere

# Single reports, cannot recreate, need to wait for more reports

- not receiving key items?
- scientist nathan no text after battle?
- ranger claude talking french after battle?
- Some hidden items are not checkable immediately?
- grunt in pinwheel forest with vanilla dragon skull not talking anymore after obtaining the dragon skull
- stone grunts not disappearing?
- sequence break problem with npcs not moving, see channel
- incredibly low catch chances? idk how that could be related to the apworld in any way
- plando items having issues? plandoing basic badge into abyssal ruins sometimes raises fillerrors about this item not being placeable
- liberty garden blackscreen
