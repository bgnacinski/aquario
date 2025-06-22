# aquario
Aquario is a all-round solution for automatic garden watering

## watering-controller
In this case the controller is based on Raspberry Pi Zero W, which controls the valves.
Communication is done through MQTT.

### Setup
Clone the `rpi-controller` directory into the `/opt/`(so that the repository is in `/opt/aquario`), then run the `deploy.sh` script.
Then change `config.json` so that the script can connect and receive messages from MQTT server.

The controller will subscribe to `<topic-prefix>/<client_id>` topic and publish to `<topic-prefix>/<status>`.