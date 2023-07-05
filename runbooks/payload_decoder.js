/**
 * Decodes the message received through the uplink
 * @param {String} input     A series of bytes
 * @returns                  Decoded data or warnings or errors
 */
function decodeUplink(input) {
    // Sensor readings
    if (input.fPort === 1) {
        if (input.bytes.length !== 10) {
            return {
                data: [],
                warnings: [],
                errors: ["fPort1: Invalid input length. Got " + input.bytes.length + " bytes, expected 10 bytes"]
            };
        }
        let sensorReadings = {};
        sensorReadings.temperature = input.bytes[0];
        sensorReadings.humidity = input.bytes[1];
        sensorReadings.co2 = input.bytes[2];
        sensorReadings.pressure = input.bytes[3];
        sensorReadings.voltage = input.bytes[4];
        sensorReadings.PM10 = input.bytes[5];
        sensorReadings.PM25 = input.bytes[6];
        sensorReadings.PM100 = input.bytes[7];
        sensorReadings.loc_x = input.bytes[8];
        sensorReadings.loc_y = input.bytes[9]; 

        return {
            data: {
                temperature: sensorReadings.temperature / 2,
                humidity: sensorReadings.humidity,
                co2: sensorReadings.co2 * 10,
                pressure: sensorReadings.pressure + 800,
                voltage: sensorReadings.voltage / 10,
                PM10: sensorReadings.PM10,
                PM25: sensorReadings.PM25,
                PM100: sensorReadings.PM100,
                loc_x: sensorReadings.loc_x,
                loc_y: sensorReadings.loc_y
            },
            warnings: [],
            errors: []
        };
    }

    // Path and location of the robot
    if (input.fPort === 2) {
        let path = [];
        for (let i = 0; i < input.bytes.length; i = i + 2) {
            path.push([input.bytes[i], input.bytes[i + 1]]);
        }

        return {
            data: path,
            warnings: [],
            errors: []
        };

    }

    // Error codes
    if (input.fPort === 3) {
        if (input.bytes.length !== 2) {
            return {
                data: [],
                warnings: [],
                errors: ["fPort3: Invalid input length, got " + input.bytes.length + " bytes, expected 2 bytes"]
            };
        }
        return {
            data: [input.bytes[0], input.bytes[1]],
            warnings: [],
            errors: []
        }
    }

    // Location of the robot
    if (input.fPort === 4) {
        if (input.bytes.length !== 2) {
            return {
                data: [],
                warnings: [],
                errors: ["fPort4: Invalid input length, got " + input.bytes.length + " bytes, expected 2 bytes"]
            };
        }
        return {
            data: [input.bytes[0], input.bytes[1]],
            warnings: [],
            errors: []
        }
    }
}






