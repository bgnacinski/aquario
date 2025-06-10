# aquario
Aquario is a all-round solution for automatic garden watering

## watering-controller
In my case based on Raspberry Pi Zero W. Controls the valves, reads schedule from a `json` file.
Communication is done through MQTT

### Setup
Clone this repository in `/opt/`(so that the repository is int `/opt/aquario`), then run the `deploy.sh` script.