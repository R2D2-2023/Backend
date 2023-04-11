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


function createCharts(graphs) {
    charts = [];
    for (let i = 0; i < graphs.length; i++) {
        charts.push(createGraph(graphs[i]));
    }
    return charts;
}

function createGraph(graph) {
    const canvas = document.getElementById(graph.canvasID);
    time_luxon = []
    for (dt of graph.time_labels) {
        time_luxon.push(luxon.DateTime.fromISO(dt))
    }

    return new Chart(canvas, {
        type: 'line',
        data: {
            labels: time_luxon,
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
                x: { display: true, title: { display: false }, type: 'time', time: { displayFormats: { hour: "dd/LL HH'h'", } } },
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



function prepend(value, array) {
    var newArray = array.slice();
    newArray.unshift(value);
    return newArray;
}

function getNewData(charts, graphs, location) {
    console.log(graphs[0].time_labels[0]);
    $.ajax({
        url: "/get_new_data",
        type: "GET",
        data: {'last_datapoint':graphs[0].time_labels[0], 'location':location},
        success: function(ret_data) {
            if (ret_data) {
                console.log(ret_data);
                console.log(ret_data['timestamp'].length);
                for (var i = 0; i < ret_data['timestamp'].length; i++) {
                    console.log(ret_data['data']);
                    console.log(ret_data['timestamp'][i]);
                    for (let j = 0; j < charts.length; j++) {
                        chart = charts[j];
                        graph = graphs[j];
                        console.log(ret_data['data'][graph.type])
                        chart.data.datasets[0].data = prepend(ret_data['data'][graph.type], chart.data.datasets[0].data);
                        chart.data.labels = prepend(luxon.DateTime.fromISO(ret_data['timestamp'][i]), chart.data.labels);
                        chart.data.datasets[0].data.pop();
                        chart.data.labels.pop();
                        graph.time_labels = prepend(ret_data['timestamp'][i], graph.time_labels);
                    }
                    
                }
                for (let i = 0; i < charts.length; i++) charts[i].update();
            }
        }
    });
}