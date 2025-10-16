# BrightSky Weather Integration for Home Assistant

This integration utilizes the free [BrightSky API](https://brightsky.dev/) to provide weather data from the German Weather Service (DWD) in Home Assistant.

## Features

- Current weather data and forecasts without API key
- Daily and hourly forecasts
- Weather entity with detailed attributes
- Sensor entities for all available weather data
- Optimized for German weather conditions and units

## Installation

### HACS (recommended)

1. Add this repository as a Custom Repository in HACS:
   - Go to HACS > Integration > Three-dot menu > Custom Repository
   - Paste the following URL: `https://github.com/dirkclemens/brightsky-ha`
   - Select Category: Integration

2. Search for "BrightSky Weather" and install it

3. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Extract the contents to the folder `custom_components/brightsky` in your Home Assistant configuration directory
3. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services > Integrations
2. Click on "+ Add Integration"
3. Search for "BrightSky Weather"
4. Follow the instructions in the configuration wizard

## Usage Notes

- BrightSky primarily provides **German weather data** from DWD
- Unlike many other weather APIs, BrightSky **does not require an API key**
- The data is usually updated hourly by DWD
- A scan interval of 900 seconds (15 minutes) is sufficient

## Available Data

- Temperature
- Feels-like temperature
- Humidity
- Air pressure
- Dew point
- Wind speed and direction
- Precipitation
- Cloud coverage
- Visibility
- Weather condition

## Troubleshooting

If problems occur:

1. Check the Home Assistant logs for errors related to `brightsky`
2. Make sure the specified location is in Germany for best results
3. Check the connection to the BrightSky API at https://api.brightsky.dev/status

## License

This integration is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [BrightSky](https://brightsky.dev/) for the great, free API
- [German Weather Service (DWD)](https://www.dwd.de/) for providing the open data weather information
