# Important stuff

# 0.4.0

## APWorld

- More modifiers
  - Randomize Wild Pokémon
    - Prevent overpowered pokémon 
      - Other modifiers take priority, some op species are even required all the time
      - Base stat total threshold adjustable
    - Prevent early Wonder Guard and fixed HP attacks
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
- account for levels of moves needed for evolving (ancient power, ...)
- reduce unown forms in randomization, only include forms 0-5 in ensure all obtainable
- combined goals
- allow encounter rate modifier to reduce slot count

## Rom

- fast travel npc in chargestone cave from south to north if battled N at north exit
- make mom stop the player at the door and say funny things for certain reusable tm choices
- skip musical tutorial, because some players have problems
- opelucid city fly flag only set after ghetsis scene?

## Both

- add now-possible locations
- a way to check whether map or fly menu is opened, used for switching to ow map in UT
- Running shoes as an item, making mom cutscene on route 2 a check
- maybe [redacted] is actually possible? but definitely with restrictions
- Dowsing Machine as a hard requirement for hidden items
- bgm randomization
- Early game cutscenes shortening option (skipping entire parts in script)
- move evos need access to free move relearner                          
- revamp flags for static encounters so that resetting statics doesn't reset the flag
- revamp season control to be toggleable between vanilla and changeable ingame
- AFTER EVERYTHING ELSE: check docs for up-to-date information, update tests, update location names in ut   

# Not urgent

- look through scripts and remove space checking for specific items
- fill evo method ids
- more inclusion rules
- post MonochromeScriptAssembler to ds romhacking servers
- make simple script compiler, use for starting season, season npc vanish, tmhm hunt npc vanish, and other future stuff
- change rules dict to being filled on the way
- organize imports for type hints behind TYPE_CHECKING
- BizHawk 2.11 having issues with modded gen 5 roms
- rename slot methods to cave/dust cloud/etc everywhere
- gracidea seems to only work on fateful encounters, assembly needed
- gym leader scripts control traded obedience level?
- wingull grams overworld items not disappearing
- extended location hint for challenge rock

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
- one case of goal not triggering reported in sync
- master ball seller not showing up again?
