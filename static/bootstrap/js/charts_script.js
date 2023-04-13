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

function getNewData(charts, graphs, timestamp) {
    let location = 1;
    $.ajax({
        url: "/get_new_data",
        type: "GET",
        data: {'last_datapoint': timestamp, 'location': location, 'max_data': 100},
        success: function(ret_data) {
            if (ret_data) {
                console.log(ret_data)
                for (let i = 0; i < ret_data.timestamp.length; i++) {
                    for (let j = 0; j < charts.length; j++) {
                        charts[j].data.datasets.forEach((dataset) => {
                            dataset.data.push(ret_data.data[graphs[j].type][i])
                        });
                    }                    
                    charts[0].data.labels.push(ret_data.timestamp[i])
                }
            }
            for (chart in charts) charts[chart].update()
        }
    })
}


// function getNewData(charts, graphs, location, timestamp) {
//     if (timestamp === undefined) {
//         timestamp = graphs[0].time_labels[0]
//     }
//     console.log(timestamp);
//     $.ajax({
//         url: "/get_new_data",
//         type: "GET",
//         data: {'last_datapoint':timestamp, 'location':location},
//         success: function(ret_data) {
//             if (ret_data) {
//                 // console.log(ret_data);
//                 // console.log(ret_data['timestamp'].length);
//                 let empty = false;
//                 if (charts[0].data.datasets[0].data.length == 0) empty = true;
//                 for (var i = ret_data['timestamp'].length; i > 0; i--) {
//                     for (let j = 0; j < charts.length; j++) {
//                         chart = charts[j];
//                         graph = graphs[j];
//                         // console.log(chart.data.datasets[0].data)
//                         // console.log(chart.data.labels)
//                         chart.data.datasets[0].data = prepend(ret_data['data'][graph.type][i], chart.data.datasets[0].data);
//                         chart.data.labels = prepend(luxon.DateTime.fromISO(ret_data['timestamp'][i]), chart.data.labels);
//                         if (!empty) {
//                             chart.data.datasets[0].data.pop();
//                             chart.data.labels.pop();
//                         }
//                         else{
//                         }
//                     }
//                     if (empty)

//                     graphs[0].time_labels.unshift(ret_data['timestamp'][i]);
                    
//                 }
//                 for (let i = 0; i < charts.length; i++) charts[i].update();
//             }
//         }
//     });
// }

function dateMinHours(hours) {
    d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
    d.setHours(d.getHours() - hours);
    return d.toISOString().slice(0, -1);
}