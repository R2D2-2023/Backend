function GraphData(type, canvasID, data_label, color, backgroundColor, suggestedMin, suggestedMax) {
    this.type = type;
    this.canvasID = canvasID;
    this.data = [];
    this.data_label = data_label;
    this.time_labels = [];
    this.color = color;
    this.backgroundColor = backgroundColor;
    this.suggestedMin = suggestedMin;
    this.suggestedMax = suggestedMax;
}

let min_global = 5;
let hour_global = 0;
let end_min_global = -1;
let end_hour_global = 0;
let location_global = 1023;
let liveUpdate = true;

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
function updateCharts(index) {
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

function getNewData(timestamp, cutoff_time, end_timestamp) {
    if (timestamp === undefined) {
        timestamp = charts[0].data.labels[charts[0].data.labels.length - 1];
    }
    if (end_timestamp === undefined) {
        end_timestamp = dateMinHours(end_hour_global, end_min_global);
    }
    $.ajax({
        url: "/get_new_data",
        type: "GET",
        data: {'last_datapoint': timestamp, 'first_datapoint': end_timestamp, 'location': location_global, 'max_data': 100},
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

            if (cutoff_time != undefined) {
                while (charts[0].data.labels[0] < cutoff_time) {
                    for (let i = 0; i < charts.length; i++) {
                        charts[i].data.datasets.forEach((dataset) => {
                            dataset.data.shift();
                        });
                        charts[i].data.labels.shift();
                        // graphs[i].time_labels.shift();
                    }
                }
            }
            dataAmount = charts[0].data.labels.length;
            if (dataAmount >= 100){
                Chart.defaults.datasets.line.pointRadius = 0;
            }
            else {
                Chart.defaults.datasets.line.pointRadius = 3 - dataAmount / 34;
            }
            for (let chart in charts) charts[chart].update();
            setControlsLock(false);
            
        }
    })
}

function setTimeView(hours, mins, end_hours, end_mins) {
    if ($.active === 0) {
        setControlsLock(true);
        clearGraphs();
        if (end_mins === undefined) end_mins = -1;
        if (end_hours === undefined) end_hours = 0;
        min_global = mins;
        hour_global = hours;
        end_min_global = end_mins;
        end_hour_global = end_hours;
        let date = dateMinHours(hour_global, min_global);
        let end_date = dateMinHours(end_hours, end_mins);
        if (end_mins === -1 && end_hours === 0) { // if button is used
            document.getElementById("start_time").value = date.slice(0,-7);
            document.getElementById("end_time").value = end_date.slice(0,-7);
            liveUpdate = true;
        }
        getNewData(date, undefined, end_date);
    }
}

function timeInputChanged() {
    let times = document.getElementsByClassName("time_input");
    let cur_time_ms = Math.round(Date.parse(dateMinHours()) / 60000) * 60000;
    let start_time_ms = cur_time_ms - Date.parse(times.start_time.value);
    let end_time_ms = cur_time_ms - Date.parse(times.end_time.value);
    liveUpdate = end_time_ms <= 0;
    if (start_time_ms - end_time_ms > 0) {
        let start_time_mins = start_time_ms / 60000 % 60;
        let start_time_hrs = Math.floor(start_time_ms / 3600000);
        let end_time_mins = end_time_ms / 60000 % 60;
        let end_time_hrs = Math.floor(end_time_ms / 3600000);

        setTimeView(start_time_hrs, start_time_mins, end_time_hrs, end_time_mins)
    }
}

// fill datetime selection with current datetime
function updateTimeInputValue() {
    if (liveUpdate) {
        const startDateControl = document.getElementById("start_time");
        const endDateControl = document.getElementById("end_time");
        startDateControl.value = dateMinHours(hour_global, min_global).slice(0, -7);
        endDateControl.value = dateMinHours(end_hour_global, end_min_global).slice(0, -7);
    }
}

function dateMinHours(hours, minutes) {
    if (minutes === undefined) {
        minutes = 0;
    }
    if (hours === undefined) {
        hours = 0;
    }
    let d = new Date();
    d.setMinutes(d.getMinutes() - minutes);
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    d.setHours(d.getHours() - hours);
    return d.toISOString().slice(0, -1);
}

function clearGraphs() {
    // Clear the data from the graphs and charts
    for (let i = 0; i < charts.length; i++) {
        charts[i].data.datasets[0].data = [];
        charts[i].data.labels = [];
        graphs[i].time_labels = [];
    }
}

function handleGraphButtons(){
        let cb_1 = document.getElementById("cb_1");
        let cb_2 = document.getElementById("cb_2");
        let cb_3 = document.getElementById("cb_3");
        let cb_4 = document.getElementById("cb_4");
        let cb_5 = document.getElementById("cb_5");
        let cb_6 = document.getElementById("cb_6");
        let cb_7 = document.getElementById("cb_7");
        let cb_8 = document.getElementById("cb_8");
        let cb_9 = document.getElementById("cb_9");
        let cb_10 = document.getElementById("cb_10");

        let uint16_t = 0;
        if (cb_1.checked) uint16_t += 1;
        if (cb_2.checked) uint16_t += 2;
        if (cb_3.checked) uint16_t += 4;
        if (cb_4.checked) uint16_t += 8;
        if (cb_5.checked) uint16_t += 16;
        if (cb_6.checked) uint16_t += 32;
        if (cb_7.checked) uint16_t += 64;
        if (cb_8.checked) uint16_t += 128;
        if (cb_9.checked) uint16_t += 256;
        if (cb_10.checked) uint16_t += 512;

        location_global = uint16_t;
        console.log(location_global);
        clearGraphs();
        setControlsLock(true);


        getNewData(dateMinHours(hour_global, min_global), undefined, dateMinHours(end_hour_global, end_min_global));
    }

};

function setControlsLock(locked){
    let time_controls = document.getElementById("instellingen_container").querySelectorAll(".time_input, button");
    let loc_controls = document.getElementById("content_container").querySelectorAll("input[type='checkbox']");
    for (let i = 0; i < time_controls.length; i++) {
        time_controls[i].disabled = locked;
    }
    for (let i = 0; i < loc_controls.length; i++) {
        loc_controls[i].disabled = locked;
    }
    let image = document.getElementById("instellingen_logo");
    let animation = document.getElementById("instellingen_animatie")
    image.hidden = locked; 
    animation.hidden = !locked; 
}
