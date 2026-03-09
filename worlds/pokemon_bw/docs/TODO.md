# Important stuff

- fix prevent rare encounters accepting copying slots (i.e. added rates == 0) (?)
- [ROM] ns castle seller very bad
- [ROM] opelucid city fly flag only set after ghetsis scene?
- [ROM] baker on village bridge not repeatable
- any_badge and any_tm_hm ignore logic(?, look for some way to validate if it can be placed there)
- [0.4] combined goals
- [0.4] revamp flags for static encounters so that resetting statics doesn't reset the flag
- [ROM] Johto exclusive balls still not fixed, maybe there is a boolean map somewhere in the code that allows items to appear in the bag
- Adding encounter plando on nonexistent methods on a map are still put into world.wild_encounters, leading to an error about having more encounters than encounter slots
- ADD UNIT TESTS AFTER EVERYTHING
- TEST EVERYTHING AFTERWARDS

# Not urgent

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
- route 8 bianca items logic, apparently said to be in logic without light/dark stone, but blocked by grunts wanting the stone
- damn wingull gram item balls not disappearing?
