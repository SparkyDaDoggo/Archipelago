# Important stuff

- [ROM] fix nacrene city waitress giving vanilla item AND AP item
- [ROM] undella mansion seller always 1000 prize?
- [ROM] sage in relic castle b1f invisible if going down before icirrus city events
- fix prevent rare encounters accepting copying slots (i.e. added rates == 0)
- port patch file version accepting stuff from main
- stats evolutions should require repeatable vitamins (shopping mall nine)
- encounter logic toggles (evolution, statics/gift/legendary, trade, fossils)
- extended dexsanity hints including pre evos (if evos in logic) and trade requests (if trades in logic)
- [ROM] aha incorrect prize also gives vanilla item
- [0.4] merge aha locations because flag flip reports are inconsistent
- [ROM] shopping mall nine evo items seller ends abrupt if canceled
- [ROM] ns castle seller very bad
- [ROM] make item names in custom roadblock dialogues a distinguishable color
- [ROM] fix reappearing hidden items still getting detected by dowsing machine because of original flags not being checked
- [ROM] opelucid city fly flag only set after ghetsis scene?
- [ROM] make massage lady in castelia repeatable
- [ROM] baker on village bridge not repeatable
- [ROM] make 50 levelups check in Icirrus City also send 25 levelups check
- locked placement stuff might remove wrong Item instances when using list.remove(), leading to some Item instances being placed twice somewhere while other instances are lost
- any_badge and any_tm_hm ignore other players' local_items and logic(?, look for some way to validate if it can be placed there)
- port over extended option counter from shapez 2
- combined goals
- [ROM] add flags for other statics and trades and put them as a bitfield into datastorage (for poptracker)
- [0.4] revamp flags for static encounters so that resetting statics doesn't reset the flag
- ADD UNIT TESTS AFTER EVERYTHING
- TEST EVERYTHING AFTERWARDS

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
