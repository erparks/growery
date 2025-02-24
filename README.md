# growery

growery is a automation project to monitor, water, and light plants (eventually)

## hub
The hub is the central place to receive reports and control operations

### backend
The backend of the hub receives REST request from monitors and uses that data to control devices

run with `python3 run.py`

### frontend
TBD should show plant status

run with `npm run dev`

## plant_monitor
The plant_monitor(s) report on plants and connect to valves (eventually)

push to arduino with `pio run -t upload` in the `plant_monitor` directory

monitor the serial output with `pio device monitor` and restart after each push to the device