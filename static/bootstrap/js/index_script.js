function getRecentData() {
    $.ajax({
        url: "/get_recent_data",
        type: "GET",
        success: function (ret_data) {
            let temp_value = document.getElementById("temperature-value");
            temp_value.innerHTML = ret_data['data']['temperature'];
            let humid_value = document.getElementById("humidity-value");
            humid_value.innerHTML = ret_data['data']['humidity'];
            let co2_value = document.getElementById("co2-value");
            co2_value.innerHTML = ret_data['data']['co2'];
            let pressure_value = document.getElementById("pressure-value");
            pressure_value.innerHTML = ret_data['data']['pressure'];
            let fijnstof_value = document.getElementById("fijnstof-value");
            fijnstof_value.innerHTML = ret_data['data']['pm'];
            let time_value = document.getElementById("time-value");
            time_value.innerHTML = ret_data['timestamp'];
        }
    })
}