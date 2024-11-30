//Getting current date function
document.addEventListener('DOMContentLoaded', function () {
    var dt = new Date();
    document.getElementById('schedule-date').innerHTML = dt.toLocaleDateString();
});

// Example data from database
const scheduleData = [
    { time: "17:00 - 18:00", match: "Liverpool - Manchester City", isBooked: true },
    { time: "18:00 - 19:00", match: "", isBooked: false },
    { time: "19:00 - 20:00", match: "", isBooked: false },
    { time: "20:00 - 21:00", match: "", isBooked: false },
    { time: "21:00 - 22:00", match: "", isBooked: false },
    { time: "22:00 - 23:00", match: "", isBooked: false },
];

const schedulerBody = document.getElementById('scheduler-body');

scheduleData.forEach(slot => {
    const row = document.createElement('tr');

    const timeCell = document.createElement('td');
    timeCell.innerText = slot.time;

    const matchCell = document.createElement('td');
    matchCell.innerText = slot.match || "Available";

    const actionCell = document.createElement('td');
    if (slot.isBooked) {
        actionCell.innerHTML = '<button class="booked" disabled>Booked</button>';
    } else {
        actionCell.innerHTML = '<button class="book-now">Book Now</button>';
    }

    row.appendChild(timeCell);
    row.appendChild(matchCell);
    row.appendChild(actionCell);

    schedulerBody.appendChild(row);
});
