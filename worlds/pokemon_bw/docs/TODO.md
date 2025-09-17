# Important stuff


# 0.3.3

- remove unique moves from trainer pokemon if randomized, and no option to re-enable them
- Chargestone cave make north to south shortcut open after traversing it for the first time (maybe when battled N)
- make client use guarded_write
- add npc to dragonspiral tower that tells you how to travers 2F
- rename modifiers in master ball seller to removing special chars, but adding custom values handling in option for backwards compatibility
- snap undella mansion seller prices to 500-steps
- Location alias for nidorans, need to test myself
- dexsanity logical path calculation, or instead put into regions?
- add ut compatibility version, give warning about incorrect logic if version mismatch
- look at encounter plando actually just overwriting when multiple plandos on same slot, or do they lead to logic errors due to species being checked and then overwritten
- check catchable species against DONE set of checklist and conditionally raise error
- fossils not revivable under certain conditions
- juniper only checking regional dex for locations before obtaining the national dex
- UT not loading encounter plando from slot data correctly
- change dialog of grunts on route 8, people tend to get confused
- juniper not always in lab?
- aha prizes flipped?
- shopping mall nine seller giving ? item when pressing b
- champion goal sending goal even after fighting ghetsis
- incorrect evolution logic, give warning in release notes
- case insensitivity for all optionsets, by making new class with overridden methods and have everything inheriting from that
- add detected rom header in patching process if wrong

# 0.2.2

important bug fixing update
- fossils not revivable under certain conditions
- fix pokemon master goal (see fixes from 0.3.x)
- juniper only checking regional dex for locations before obtaining the national dex
- juniper not always in lab?
- champion goal sending goal even after fighting ghetsis

# 0.4.0

- add now-possible locations
- no cost modifier in master ball seller default to 3000, and make every cost value possible via custom valid() method
- more things for encounter plando
  - "None" species for Encounter Plando, to give a chance to not plando anything
- fix bianca being spelled "Bianka" on some location names
- Merge PR adding "Randomize" to trainer/wild if other modifiers present
- add deerling forms to always required species
  - also fix that location's progress type
- More modifiers
  - Randomize Wild Pokémon
    - Prevent overpowered pokémon 
      - Gets overwritten by "Ensure all obtainable"
      - Base stat total threshold adjustable
  - Randomize Trainer Pokémon 
    - Prevent overpowered pokémon
      - Base stat total threshold adjustable
    - Force fully evolved 
      - Level threshold adjustable
- Randomization Blacklist
  - Wild pokémon 
    - This will throw an OptionError if "Ensure all obtainable" is selected and any blacklisted is base stage
  - Trainer pokémon

# Not urgent

- dig with seasons patch crashes the game, not fixable?
- look through scripts and remove space checking for specific items
- fix evo method ids
- more inclusion rules
- complete levelup movesets
- advertise on ds romhacking servers
- post MonochromeScriptAssembler to ds romhacking servers
- ask for ndspy licensing
- make simple script compiler, use for starting season, season npc vanish, tmhm hunt npc vanish, and other future stuff
- change rules dict to being filled on the way
- organize imports for type hints behind TYPE_CHECKING
- musharna encounter not appearing on first visit?
- plando items having issues? plandoing basic badge into abyssal ruins sometimes raises fillerrors regarding this item not being placeable
- pitch webhost and template yaml notes, both individual, but template copying from webhost by default
- Fix locations in pokédex if something written to encounter tables
- route 18 reappearing and undella bay reappearing items get still detected after pickup

# Single reports, cannot recreate, need to wait for more reports

- not receiving key items?
- scientist nathan no text after battle?
- ranger claude talking french after battle?
- Some hidden items are not checkable immediately?
- grunt in pinwheel forest with dragon skull not talking anymore after obtaining the dragon skull
- stone grunts not disappearing?
- sequence break problem with npcs not moving, see channel
