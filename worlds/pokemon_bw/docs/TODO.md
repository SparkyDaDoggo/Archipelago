# Important stuff

- Apricorn balls not appearing in-battle
- post ghetsis location group
- fix nacrene city waitress giving vanilla item AND AP item
- optionset descriptions: "You can include as many of the following modifiers as you want."
- randomization optionsets: add randomize if not empty (port over from main branch)
- elemental monkeys missing in ensure all obtainable?
- undella mansion seller always 1000 prize?
- sage in relic castle b1f invisible if going down before icirrus city events
- give prevent rare encounters an adjustable modifier and set its default to 8
- fix prevent rare encounters accepting copying slots (i.e. added rates == 0)
- port patch file version accepting stuff from main
- stats evolutions should require repeatable vitamins (shopping mall nine)
- encounter logic toggles (evolution, statics/gift/legendary, trade, fossils)
- extended dexsanity hints including pre evos (if evos in logic) and trade requests (if trades in logic)
- statics and trades to encounter_by_method
- aha incorrect prize also gives vanilla item
- merge aha locations because flag flip reports are inconsistent
- does "train any pokemon by 50 levels" have any additional logic? better require league/ns castle
- moor of icirrus inaccessible in winter without surf?
- shopping mall nine evo items seller ends abrupt if canceled
- ns castle seller very bad
- extended location hint for deerlings location and challenge rock
- make item names in custom roadblock dialogues a distinguishable color
- fix reappearing hidden items still getting detected by dowsing machine because of original flags not being checked
- opelucid city fly flag only set after ghetsis scene?
- make massage lady in castelia repeatable
- baker on village bridge not repeatable
- report: lv48 encounter on marvelous bridge and lv25 on route 15, despite adjust_levels
- make 50 levelups check in Icirrus City also send 25 levelups check

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
- route 18 reappearing and undella bay reappearing items get still detected after pickup
- make reusable tms option add funny dialog
- BizHawk 2.11 having issues with modded gen 5 roms
- Chargestone cave make north to south shortcut open after traversing it for the first time (maybe when battled N)
- gracidea seems to only work on fateful encounters, assembly needed
- gym leader scripts control traded obedience level?

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
- route 8 bianca items logic, apparently said to be in logic without light/dark stone, but blocked by grunts wanting the stone
- damn wingull gram item balls not disappearing?
