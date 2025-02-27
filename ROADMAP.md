# Roadmap

- HA watchdog support to allow automatic restarts
- Check for PW Leader vs Follower
  - The TEDAPI requires communication with the Leader, so this will be a critical error and exit on startup
- Interactivity
  - Right now there is no ability to control the PW.  If the TEDAPI is capable of doing this, and we can figure out how to do it, I would add these capabilities to the add-on, but both of those are very iffy.  It may require using the Tesla FleetAPI integration instead.  This add-on would still be useful to get more frequent data from the PW because Tesla charges for use of the FleetAPI based on the number of calls you make.
  - Ability to change backup reserve percentage
  - Ability to change consumption mode
  - Ability to go on and off-grid


