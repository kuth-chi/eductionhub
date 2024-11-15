document.addEventListener("DOMContentLoaded", function(){
    const dockLeft = document.getElementById("dock-left");
    const dockCenter = document.getElementById("dock-center");
    const dockRight = document.getElementById("dock-right");

    let count = 0;
    if (dockCenter) {
        dockCenter.addEventListener("click", function () {
            count++;
            console.log("count: " + count);
        });
    } else {
        console.error("dock-center element not found.");
    }
});

// Carousel Drag & Swipe logic
let isMouseDown = false;
let startX, scrollLeft;

const carousel = document.querySelector('.carousel-wrapper');

// On Mouse down, start dragging
carousel.addEventListener("mousedown", function (e) {
    isMouseDown = true;
    startX = e.pageX - carousel.getBoundingClientRect().left;  // Using getBoundingClientRect()
    scrollLeft = carousel.scrollLeft;
});

// On mouse leave or mouse up, stop dragging
carousel.addEventListener('mouseleave', () => {
    isMouseDown = false;
});

carousel.addEventListener('mouseup', () => {
    isMouseDown = false;
});

// On mouse move, drag the carousel
carousel.addEventListener('mousemove', (e) => {
    if (!isMouseDown) return;
    const x = e.pageX - carousel.getBoundingClientRect().left;
    const move = (x - startX) * 3; // Multiplier to adjust drag speed
    carousel.scrollLeft = scrollLeft - move;
});

// --- Touch Events for Swipe ---
let isTouchStart = false;
let touchStartX, touchScrollLeft;

carousel.addEventListener('touchstart', (e) => {
    isTouchStart = true;
    touchStartX = e.touches[0].pageX - carousel.getBoundingClientRect().left;  // Using getBoundingClientRect()
    touchScrollLeft = carousel.scrollLeft;
});

carousel.addEventListener('touchend', (e) => {
    isTouchStart = false;
});

carousel.addEventListener('touchmove', (e) => {
    if (!isTouchStart) return;
    e.preventDefault();  // Prevent scrolling while swiping
    const x = e.touches[0].pageX - carousel.getBoundingClientRect().left;
    const move = (x - touchStartX) * 3; // Multiplier to adjust swipe speed
    carousel.scrollLeft = touchScrollLeft - move;
});
