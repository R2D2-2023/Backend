function addNotification(message) {
    var notificationContainer = document.querySelector('.notification-container');
    var notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
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

// Example usage: add a new notification        
for (let i = 1; i < 51; i++) {
    message = i + " notif";
    addNotification(message); 
}
