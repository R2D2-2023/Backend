let menu = document.querySelector('#menu-icon');
let navlist = document.querySelector('.navlist');

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navlist.classList.toggle('open');
};

const sr = ScrollReveal({
    distance: '65px',
    duration: 2600,
    delay: 450,
    reset: true
});

sr.reveal('.hero-text', { delay: 100, origin: 'top' });
sr.reveal('.hero-image', { delay: 100, origin: 'top' });





var checkboxes = document.querySelectorAll("input [type = 'checkbox']");
function checkAll(myCheckbox) {
    if (myCheckbox.checked == true) {
        checkboxes.forEach(function (checkbox) {
            checkbox.checked = true;
        });
    }
}