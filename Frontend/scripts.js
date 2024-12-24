//Getting current date function
document.addEventListener('DOMContentLoaded', function () {
    var dt = new Date();
    document.getElementById('schedule-date').innerHTML = dt.toLocaleDateString();
});
// Function to fetch timeslot data from the backend
document.addEventListener('DOMContentLoaded', fetchTimeslotData);

async function fetchTimeslotData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/timeslot'); // Update with your backend URL if different
        const result = await response.json();

        if (result.success) {
            const scheduleData = result.data; // Data fetched from the backend
            populateScheduler(scheduleData);
        } else {
            console.error("Error fetching timeslot data:", result.error);
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Function to populate the scheduler table
function populateScheduler(scheduleData) {
    const schedulerBody = document.getElementById('scheduler-body');
    schedulerBody.innerHTML = ''; // Clear existing rows

    scheduleData.forEach(slot => {
        const row = document.createElement('tr');

        const timeCell = document.createElement('td');
        timeCell.innerText = `${slot.StartTime} - ${slot.EndTime}`;

        const matchCell = document.createElement('td');
        if (slot.Team1Name && slot.Team2Name) {
            matchCell.innerText = `${slot.Team1Name} - ${slot.Team2Name}`;
        } else {
            matchCell.innerText = "Available";
        }

        const actionCell = document.createElement('td');
        if (slot.IsBooked) {
            actionCell.innerHTML = '<button class="booked" disabled>Booked</button>';
        } else {
            actionCell.innerHTML = '<button class="book-now">Book Now</button>';
        }

        row.appendChild(timeCell);
        row.appendChild(matchCell);
        row.appendChild(actionCell);

        schedulerBody.appendChild(row);
    });
}

// Call the function to fetch data when the page loads

/*
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
*/

//LIST OF TEAMS ASKING FOR MATCH
document.addEventListener('DOMContentLoaded', function () {
    loadMatchRequestTeams();
});

async function loadMatchRequestTeams() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/teams-asking-for-match');
        const result = await response.json();

        if (result.success) {
            const teams = result.data;
            const teamList = document.getElementById('match-request-team-list');
            teamList.innerHTML = ''; // Clear any existing data

            teams.forEach(team => {
                const listItem = document.createElement('li');
                listItem.textContent = team.Name;
                teamList.appendChild(listItem);
            });
        } else {
            console.error('Failed to load teams:', result.error);
        }
    } catch (error) {
        console.error('Error fetching teams:', error);
    }
}
//Booking PopUp
document.addEventListener('DOMContentLoaded', () => {
    // Get modal and elements
    const modal = document.getElementById('booking-modal');
    const closeModal = modal.querySelector('.close');
    const bookingForm = document.getElementById('booking-form');
    const timeslotInput = document.getElementById('timeslot'); // Timeslot input field in modal
  
    // Add event listeners to "Book Now" buttons
    document.querySelectorAll('.book-now').forEach((button, index) => {
      button.addEventListener('click', (event) => {
        const timeslot = event.target.closest('tr').querySelector('td').innerText; // Get timeslot from table row
        timeslotInput.value = timeslot; // Set timeslot value in the modal
        modal.style.display = 'flex'; // Show the modal
      });
    });
  
    // Close modal
    closeModal.addEventListener('click', () => {
      modal.style.display = 'none';
    });
  
    // Submit booking form
    bookingForm.addEventListener('submit', async (e) => {
      e.preventDefault();
  
      const formData = new FormData(bookingForm);
      const bookingData = {
        team1: formData.get('team1'),
        team2: formData.get('team2'),
        timeslot: formData.get('timeslot'),
      };
  
      try {
        const response = await fetch('/booking', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(bookingData),
        });
        
        const result = await response.json();
        if (result.success) {
          alert('Booking successful!');
        } else {
          alert('Booking failed: ' + result.error);
        }
      } catch (error) {
        alert('Error submitting booking: ' + error.message);
      }
  
      modal.style.display = 'none';
    });
  });

document.addEventListener('DOMContentLoaded', fetchLeagueTableData);
async function fetchLeagueTableData() {
    const response = await fetch('http://127.0.0.1:5000/rankings');
    const result = await response.json();

    if (result.success) {
        const tableBody = document.getElementById('table-body');
        tableBody.innerHTML = ''; // Clear previous rows

        result.data.forEach((team, index) => {
            const row = document.createElement('tr');

            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${team.Club}</td>
                <td>${team.Played}</td>
                <td>${team.Won}</td>
                <td>${team.Lost}</td>
                <td>${team.Drawn}</td>
                <td>${team.GF}</td>
                <td>${team.GA}</td>
                <td>${team['Win %']}</td>
            `;

            tableBody.appendChild(row);
        });
    }
}
