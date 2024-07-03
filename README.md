# Concretize

Concretize turns scenarios for testing autonomous vehicles specified using a domain-specific modelling language into concrete scenes. It offers diagram generation using [Scenic](https://github.com/BerkeleyLearnVerify/Scenic) and integration with [CARLA](https://carla.org/) for simulation.

## How to install

1. Install [Docker](https://docs.docker.com/get-docker/)
2. Clone this repository
3. Open the root folder of this repository, and run `docker-compose build` then `docker-compose up`. If you are using Linux, you may need to add `sudo` before these commands.
4. Navigate to [https://localhost:5173](https://localhost:5173) in your browser to see the web interface. An up-to-date Chromium-based browser is recommended to ensure correct display.

## For more information
See the [Wiki](https://github.com/ArenBabikian/concretize/wiki) for more documentation, including
- [Scenario specification language](https://github.com/ArenBabikian/concretize/wiki/Scenario-Specification-Language)
