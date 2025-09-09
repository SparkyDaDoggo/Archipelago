# Setup Guide for Pokémon Black and White: Archipelago

## Important

As we are using BizHawk, this guide is only applicable to Windows and Linux systems. 
This APWorld is still in development, so expect bugs! 
If you find one, please report it to the #future-game-design thread for this game!

## Required Software

- BizHawk: [Bizhawk Releases from TASVideos](https://tasvideos.org/BizHawk/ReleaseHistory)
  - Version 2.10 is recommended
  - **Important**: Upon opening the emulator for the first time, go to `Config > Customize... > Advanced` 
    and **disable** `AutoSaveRam`. Else, save data might not be properly saved.
  - Detailed installation instructions for BizHawk can be found at the above link.
  - Windows users must run the prerequisite installer first, which can also be found at the above link.
- The built-in BizHawk client within the Archipelago software, which can be found 
  [here](https://github.com/ArchipelagoMW/Archipelago/releases)
- A .nds file for the english version of Pokémon Black and White
  - The english versions for USA and Europe are the same

## Optional Software

- BizhHawk Client w/ Universal Tracker: 
  - [BizHawk Client w/ Universal Tracker Version 1.3.0](https://github.com/Rurusachi/Archipelago/releases/tag/BizhawkUT_1.3.0) —
    There is no Poptracker pack for this apworld at the moment, however there is
    limited map support for Universal Tracker. **Requires**: Latest compatible version of [Universal Tracker](https://github.com/FarisTheAncient/Archipelago/releases/tag/Tracker_v0.2.14).
  - Both Universal Tracker and the BizHawk Client w/ Universal Tracker apworlds must be added to your `custom_worlds`
    folder in your Archipelago install. They should not be in `lib/worlds`.

## Generating and Patching a Game

1. Add `pokemon_bw.apworld` to your `custom_worlds` folder in your Archipelago install. It should not be in
   `lib/worlds`.
2. Create your options file (YAML). You can make one by choosing `Generate Templates`
   from the Archipelago Launcher. From there, you can edit the `.yaml` in any text editor.
3. Follow the general Archipelago instructions for [generating a game on your local installation](https://archipelago.gg/tutorial/Archipelago/setup/en#on-your-local-installation).
   This will generate an output file for you. Your patch file will have the `.apblack` or `.apwhite` file extension 
   and will be inside the output file.
4. Open `ArchipelagoLauncher.exe`
5. Select "Open Patch" on the left side and select your patch file.
6. If this is your first time patching, you will be prompted to locate your vanilla ROM.
7. A patched `.nds` file will be created in the same place as the patch file.
8. On your first time opening a patch with BizHawk Client, you will also be asked to locate `EmuHawk.exe` in your
   BizHawk install.

If you're playing a single-player seed, and you don't care about autotracking or hints, you can stop here, close the
client, and load the patched ROM in any emulator. However, for multiworlds and other Archipelago features, continue
below using BizHawk as your emulator.

## Connecting to a Server

By default, opening a patch file will do steps 1-5 below for you automatically. Even so, keep them in your memory just
in case you have to close and reopen a window mid-game for some reason.

1. Pokémon Black & White uses Archipelago's BizHawk Client. If the client isn't still open from when you patched your game,
you can re-open it from the launcher.
2. Ensure EmuHawk is running the patched ROM.
3. In EmuHawk, go to `Tools > Lua Console`. This window must stay open while playing.
4. In the Lua Console window, go to `Script > Open Script…`.
5. Navigate to your Archipelago install folder and open `data/lua/connector_bizhawk_generic.lua`.
6. The emulator and client will eventually connect to each other. The BizHawk Client window should indicate that it
connected and recognized Pokémon Black & White.
7. To connect the client to the server, enter your room's address and port (e.g. `archipelago.gg:38281`) into the
top text field of the client and click Connect. An alternative way to connect is typing `/connect <address>:<port> [password]` into the bottom text field and then typing your slot name (if prompted).

You should now be able to receive and send items. You'll need to do these steps every time you want to reconnect. It is
perfectly safe to make progress offline; everything will re-sync when you reconnect.
