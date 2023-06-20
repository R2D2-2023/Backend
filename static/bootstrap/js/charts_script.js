function GraphData(type, canvasID, data, data_label, time_labels, color, backgroundColor, suggestedMin, suggestedMax) {
    this.type = type;
    this.canvasID = canvasID;
    this.data = data;
    this.data_label = data_label;
    this.time_labels = time_labels;
    this.color = color;
    this.backgroundColor = backgroundColor;
    this.suggestedMin = suggestedMin;
    this.suggestedMax = suggestedMax;
}

var min_global = 2;
var hour_global = 0;

function createCharts(graphs) {
    charts = [];
    for (let i = 0; i < graphs.length; i++) {
        charts.push(createGraph(graphs[i]));
    }
    return charts;
}

function createGraph(graph) {
    const canvas = document.getElementById(graph.canvasID);

    return new Chart(canvas, {
        type: 'line',
        data: {
            labels: graph.time_labels,
            datasets: [{
                label: graph.data_label,
                data: graph.data,                           // de data die je laat zien
                borderColor: graph.color,                   // kleur van de lijn
                backgroundColor: graph.backgroundColor,     // vul kleur van de bolletjes en blokjes
                fill: false,                                // de onderkant vullen
                cubicInterpolationMode: 'monotone',         // de vorm van de lijn afronden
                tension: 0.4,                               // hoeveel er word afgerond
                borderWidth: 1                              // dikte van de lijn
            }]
        },
        options: {
            responsive: true,
            animation: false,
            interaction: {
                intersect: false,
            },
            scales: {
                x: { display: true, title: { display: false }, type: 'time', time: { displayFormats: { hour: "dd/LL HH'h'", minute: "HH:mm", second: "HH:mm:ss" } }, ticks: {maxTicksLimit: 10} },
                y: { display: true, title: { display: false, text: 'Degrees celsius (°C)' }, suggestedMin: graph.suggestedMin, suggestedMax: graph.suggestedMax, }
            }
        }
    });


}


// function to update the graph with new data
function updateCharts(charts, graphs, index) {
    document.getElementById('myRange').value=index
    // update the chart data
    for (let i = 0; i < charts.length; i++) {
        chart = charts[i];
        graph = graphs[i];
        chart.data.datasets[0].data = graph.data.slice(0, index);
        chart.data.labels = graph.time_labels.slice(0, index);
        chart.update();
    }
}

function append(value, array) {
    var newArray = array.slice();
    newArray.shift(value);
    return newArray;
}

function prepend(value, array) {
    var newArray = array.slice();
    newArray.unshift(value);
    return newArray;
}

function getNewData(charts, graphs, location, timestamp, cutoff_time) {
    if (timestamp === undefined) {
        timestamp = charts[0].data.labels[charts[0].data.labels.length - 1]
    }
    $.ajax({
        url: "/get_new_data",
        type: "GET",
        data: {'last_datapoint': timestamp, 'location': location, 'max_data': 100},
        success: function(ret_data) {
            if (typeof ret_data === 'object') {
                for (let i = 0; i < ret_data.timestamp.length; i++) {
                    for (let j = 0; j < charts.length; j++) {
                        charts[j].data.datasets.forEach((dataset) => {
                            dataset.data.push(ret_data.data[graphs[j].type][i])
                        });
                        charts[j].data.labels.push(ret_data.timestamp[i])
                    }                    
                }
            }
            else {
            }
            if (cutoff_time != undefined) {
                while (charts[0].data.labels[0] < cutoff_time) {
                    for (let i = 0; i < charts.length; i++) {
                        charts[i].data.datasets.forEach((dataset) => {
                            dataset.data.shift();
                        });
                        charts[i].data.labels.shift();
                        // graphs[i].ti me_labels.shift();
                    }
                }
            }
            for (let chart in charts) charts[chart].update();
        }
    })
}

function setTimeView(charts, graphs, location, hours, mins) {
    // Clear the data from the graphs and charts
    for (let i = 0; i < charts.length; i++) {
        charts[i].data.datasets[0].data = [];
        charts[i].data.labels = [];
        graphs[i].time_labels = [];
    }
    min_global = mins;
    hour_global = hours;
    getNewData(charts, graphs, location, dateMinHours(hour_global, min_global), undefined);
}

function dateMinHours(hours, minutes) {
    if (minutes === undefined) {
        minutes = 0;
    }
    if (hours === undefined) {
        hours = 0;
    }
    d = new Date();
    d.setMinutes(d.getMinutes() - minutes);
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    d.setHours(d.getHours() - hours);
    return d.toISOString().slice(0, -1);
}