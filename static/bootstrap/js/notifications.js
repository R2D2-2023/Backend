var last_entry = 0;

function addNotification(message) {
    var notificationContainer = document.querySelector('.notification-container');
    var notification = document.createElement('div');
    notification.className = 'notification';
    var id = document.createElement('div');
    var text = document.createElement('div');
    id.textContent = message;
    text.textContent = "1";
    notification.insertBefore(id, notification.firstChild);
    notification.insertBefore(text, notification.firstChild);
    notificationContainer.insertBefore(notification, notificationContainer.firstChild);
    notificationContainer.scrollTop = 0;
}

var notificationContainer = document.querySelector('.notification-container');
notificationContainer.addEventListener('scroll', function() {
    notificationContainer.classList.remove('unselectable');
});

// JavaScript to enable clicking and scrolling within the container
var notificationContainer = document.querySelector('.notification-container');
var isMouseDown = false;
var startX;
var startY;

notificationContainer.addEventListener('mousedown', function(event) {
    isMouseDown = true;
    startX = event.clientX;
    startY = event.clientY;
    document.body.classList.add('disable-selection');
});

document.addEventListener('mouseup', function() {
    isMouseDown = false;
    document.body.classList.remove('disable-selection');
});

document.addEventListener('mousemove', function(event) {
    if (isMouseDown) {
        var dx = event.clientX - startX;
        var dy = event.clientY - startY;
        notificationContainer.scrollTop -= dy;
        startX = event.clientX;
        startY = event.clientY;
    }
});

function checkForNotif() {
    $.ajax({
        url: '/get_latest_entry',
        type: 'GET',
        success: function(response) {
            for (var i = 0; i < response.data.length; i++) {
                var id = response.data[i].id;
                var error = response.data[i].message;

                var message = id + '\n' + error;
                if (last_entry === 0 || last_entry < id) {
                    last_entry = id;
                    addNotification(message);
                }    
            }
        },
    });
}