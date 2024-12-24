//check login
document.addEventListener("DOMContentLoaded", function () {
    const loggedIn = localStorage.getItem("loggedIn");
    if (loggedIn !== "true") {
        // User is not logged in, redirect to login page
        window.location.href = "login.html";
    }
});

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
    document.getElementById('scheduler-body').addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('book-now')) {
            const timeslot = event.target.closest('tr').querySelector('td').innerText; // Get timeslot from table row
            timeslotInput.value = timeslot; // Set timeslot value in the modal
            modal.style.display = 'flex'; // Show the modal
        }
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
          team1: localStorage.getItem("loggedInEmail"),
          team2: formData.get('team'),
          timeslot: formData.get('timeslot'),
      };
  
      try {
        const response = await fetch('http://127.0.0.1:5000/booking', {
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
//ADMIN PANEL FUNCTIONS
// Load teams
document.addEventListener('DOMContentLoaded', loadTeams);

async function loadTeams() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/teams');
        const result = await response.json();

        if (result.success) {
            const teamTableBody = document.getElementById('team-management-table').getElementsByTagName('tbody')[0];
            teamTableBody.innerHTML = '';

            result.data.forEach(team => {
                const row = document.createElement('tr');

                row.innerHTML = `
                    <td>${team.Name}</td>
                    <td>${team.Email}</td>
                    <td>
                        <button class="delete-team" data-id="${team.TeamID}">Delete</button>
                        <button class="edit-team" data-id="${team.TeamID}" data-name="${team.Name}" data-email="${team.Email}">Edit</button>
                    </td>
                `;

                teamTableBody.appendChild(row);
            });

            attachTeamActions();
        } else {
            console.error('Error fetching teams:', result.error);
        }
    }
    catch (error) {
        console.error('Error loading teams:', error);
    }
}

// Add action to the edit and delete buttons
function attachTeamActions() {
    document.querySelectorAll('.delete-team').forEach(button => {
        button.addEventListener('click', async (event) => {
            const teamId = event.target.dataset.id;
            if (confirm('Are you sure you want to delete this team?')) {
                await deleteTeam(teamId);
                loadTeams();
            }
        });
    });

    document.querySelectorAll('.edit-team').forEach(button => {
        button.addEventListener('click', (event) => {
            const teamId = event.target.dataset.id;
            const teamName = event.target.dataset.name;
            const teamEmail = event.target.dataset.email;

            const newName = prompt('Enter new team name:', teamName);
            const newEmail = prompt('Enter new email:', teamEmail);

            if (newName && newEmail) {
                updateTeam(teamId, newName, newEmail);
            }
        });
    });
}

// Delete the team
async function deleteTeam(teamId) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/teams/${teamId}`, {
            method: 'DELETE',
        });
        const result = await response.json();
        if (result.success) {
            alert('Team deleted successfully');
        } else {
            alert('Failed to delete team: ' + result.error);
        }
    } catch (error) {
        console.error('Error deleting team:', error);
    }
}

// Edit the team
async function updateTeam(teamId, name, email) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/teams/${teamId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email }),
        });
        const result = await response.json();
        if (result.success) {
            alert('Team updated successfully');
            loadTeams();
        } else {
            alert('Failed to update team: ' + result.error);
        }
    } catch (error) {
        console.error('Error updating team:', error);
    }
}

// Load match score informations
document.addEventListener('DOMContentLoaded', loadMatchScores);

async function loadMatchScores() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/matches');
        const result = await response.json();

        if (result.success) {
            const matchTableBody = document.getElementById('match-score-table').getElementsByTagName('tbody')[0];
            matchTableBody.innerHTML = '';

            result.data.forEach(match => {
                const row = document.createElement('tr');

                row.innerHTML = `
                    <td>${match.Team1Name} vs ${match.Team2Name}</td>
                    <td><input type="number" class="score-input" data-match-id="${match.MatchID}" data-team="1" value="${match.Score1 || ''}" /></td>
                    <td><input type="number" class="score-input" data-match-id="${match.MatchID}" data-team="2" value="${match.Score2 || ''}" /></td>
                    <td><button class="save-score" data-match-id="${match.MatchID}">Save</button></td>
                `;

                matchTableBody.appendChild(row);
            });

            attachSaveActions();
        } else {
            console.error('Error fetching match scores:', result.error);
        }
    } catch (error) {
        console.error('Error loading match scores:', error);
    }
}

// Add action the save button
function attachSaveActions() {
    document.querySelectorAll('.save-score').forEach(button => {
        button.addEventListener('click', async (event) => {
            const matchId = event.target.dataset.matchId;
            const score1 = document.querySelector(`.score-input[data-match-id="${matchId}"][data-team="1"]`).value;
            const score2 = document.querySelector(`.score-input[data-match-id="${matchId}"][data-team="2"]`).value;

            if (score1 !== '' && score2 !== '') {
                await saveMatchScore(matchId, score1, score2);
            } else {
                alert('Please enter both scores.');
            }
        });
    });
}

// Save the scores
async function saveMatchScore(matchId, score1, score2) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/matches/${matchId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ score1, score2 }),
        });

        const result = await response.json();

        if (result.success) {
            alert('Scores updated successfully');
            loadMatchScores();
        } else {
            alert('Failed to update scores: ' + result.error);
        }
    } catch (error) {
        console.error('Error saving match score:', error);
    }
}
// Load all timeslots
document.addEventListener('DOMContentLoaded', loadTimeslots);

async function loadTimeslots() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/timeslots');
        const result = await response.json();

        if (result.success) {
            const timeslotTableBody = document.getElementById('timeslot-management-table').getElementsByTagName('tbody')[0];
            timeslotTableBody.innerHTML = '';

            result.data.forEach(timeslot => {
                const row = document.createElement('tr');

                row.innerHTML = `
                    <td>${timeslot.StartTime} - ${timeslot.EndTime}</td>
                    <td>${timeslot.IsBooked ? 'Booked' : 'Available'}</td>
                    <td>
                        <button class="delete-timeslot" data-id="${timeslot.TimeSlotID}">Delete</button>
                    </td>
                `;

                timeslotTableBody.appendChild(row);
            });

            attachTimeslotActions();
        } else {
            console.error('Error fetching timeslots:', result.error);
        }
    } catch (error) {
        console.error('Error loading timeslots:', error);
    }
}

// Add deleting actions
function attachTimeslotActions() {
    document.querySelectorAll('.delete-timeslot').forEach(button => {
        button.addEventListener('click', async (event) => {
            const timeslotId = event.target.dataset.id;
            if (confirm('Are you sure you want to delete this timeslot?')) {
                await deleteTimeslot(timeslotId);
                loadTimeslots(); // Tabloyu yenile
            }
        });
    });
}

// Delete the timeslot
async function deleteTimeslot(timeslotId) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/timeslots/${timeslotId}`, {
            method: 'DELETE',
        });
        const result = await response.json();
        if (result.success) {
            alert('Timeslot deleted successfully');
        } else {
            alert('Failed to delete timeslot: ' + result.error);
        }
    } catch (error) {
        console.error('Error deleting timeslot:', error);
    }
}

