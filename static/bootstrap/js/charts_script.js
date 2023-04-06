// src = "https://cdn.jsdelivr.net/npm/chart.js@4.2.1";
// src = "https://cdn.jsdelivr.net/npm/luxon@3.3.0/build/global/luxon.js";
// src = "https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@^1.3.1";

const ct1 = document.getElementById('tempChart');
time_labels = {{ get_recent_sensor_readings(0, 100) | safe }}
time_luxon = []
for (dt of time_labels) {
    time_luxon.push(luxon.DateTime.fromISO(dt))
}
temp_data = {{ get_recent_sensor_readings(1, 100) | safe }}

chart = new Chart(ct1, {
    type: 'line',
    data: {
        labels: time_luxon,
        datasets: [{
            label: 'Temperature (°C)',
            data: temp_data,
            borderWidth: 1
        }]
    },

    options: {
        animation: false,
        scales: {
            x: {
                type: 'time',
                time: {
                    displayFormats: {
                        hour: "dd/LL HH'h'",
                    }
                }
            },
            y: {
                suggestedMin: 20,
                suggestedMax: 30,
            }
        }
    }
});


const ct2 = document.getElementById('co2Chart');
time_labels = {{ get_recent_sensor_readings(0, 100) | safe }}
time_luxon = []
for (dt of time_labels) {
    time_luxon.push(luxon.DateTime.fromISO(dt))
}
co2_data = {{ get_recent_sensor_readings(2, 100) | safe }}

chart2 = new Chart(ct2, {
    type: 'line',
    data: {
        labels: time_luxon,
        datasets: [{
            label: 'CO2 (ppm)',
            borderColor: '#FF396A',
            backgroundColor: '#FF396A80',
            data: co2_data,
            borderWidth: 1
        }]
    },
    options: {
        animation: false,
        scales: {
            x: {
                type: 'time',
                time: {
                    displayFormats: {
                        hour: "dd/LL HH'h'",
                    }
                }
            },
            y: {
                suggestedMin: 400,
                suggestedMax: 1000,
            }
        }
    }
});

const ct3 = document.getElementById('humidChart');
time_labels = {{ get_recent_sensor_readings(0, 100) | safe }}
time_luxon = []
for (dt of time_labels) {
    time_luxon.push(luxon.DateTime.fromISO(dt))
}
humid_data = {{ get_recent_sensor_readings(3, 100) | safe }}

chart3 = new Chart(ct3, {
    type: 'line',
    data: {
        labels: time_luxon,
        datasets: [{
            label: 'Humidity (%)',
            borderColor: '#39CF6A',
            backgroundColor: '#39CF9A80',
            data: humid_data,
            borderWidth: 1
        }]
    },
    options: {
        animation: false,
        scales: {
            x: {
                type: 'time',
                time: {
                    displayFormats: {
                        hour: "dd/LL HH'h'",
                    }
                }
            },
            y: {
                suggestedMin: 40,
                suggestedMax: 60,
            }
        }
    }
});

const ct4 = document.getElementById('presChart');
time_labels = {{ get_recent_sensor_readings(0, 100) | safe }}
time_luxon = []
for (dt of time_labels) {
    time_luxon.push(luxon.DateTime.fromISO(dt))
}
pres_data = {{ get_recent_sensor_readings(4, 100) | safe }}

chart4 = new Chart(ct4, {
    type: 'line',
    data: {
        labels: time_luxon,
        datasets: [{
            label: 'Air pressure (hPa)',
            borderColor: '#FFAA00',
            backgroundColor: '#FFAA0080',
            data: pres_data,
            borderWidth: 1
        }]
    },
    options: {
        animation: false,
        scales: {
            x: {
                type: 'time',
                time: {
                    displayFormats: {
                        hour: "dd/LL HH'h'",
                    }
                }
            },
            y: {
                suggestedMin: 1000,
                suggestedMax: 1100,
            }
        }
    }
});



// function to update the graph with new data
function updateGraph(index) {
    document.getElementById('myRange').value = index
    // update the chart data
    chart.data.datasets[0].data = temp_data.slice(index, 100);
    chart.data.labels = time_labels.slice(index, 100);
    chart2.data.datasets[0].data = co2_data.slice(index, 100);
    chart2.data.labels = time_labels.slice(index, 100);
    chart3.data.datasets[0].data = humid_data.slice(index, 100);
    chart3.data.labels = time_labels.slice(index, 100);
    chart4.data.datasets[0].data = pres_data.slice(index, 100);
    chart4.data.labels = time_labels.slice(index, 100);
    // update the chart
    chart.update();
    chart2.update();
    chart3.update();
    chart4.update();
}