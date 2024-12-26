//check login
document.addEventListener("DOMContentLoaded", function () {
    const loggedIn = localStorage.getItem("loggedIn");
    if (loggedIn !== "true") {
        // User is not logged in, redirect to login page
        window.location.href = "login.html";
    }
});
//Logout Button
document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("click", (event) => {
        const logoutBtn = event.target.closest("#logout-btn");
        if (logoutBtn) {
            // Clear user session data
            localStorage.removeItem("loggedIn");
            localStorage.removeItem("loggedInEmail");

            // Redirect to login page
            window.location.href = "../Frontend/login.html"; // Adjust path as needed
        }
    });
});

/*
document.addEventListener("DOMContentLoaded", () => {
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        console.log("Logout button found in the DOM.");
        logoutBtn.addEventListener("click", () => {
            // Clear user session data
            localStorage.removeItem("loggedIn");
            localStorage.removeItem("loggedInEmail");

            // Redirect to login page
            window.location.href = "./login.html";

        });
    }
});

 */
//Getting current date function
document.addEventListener('DOMContentLoaded', function () {
    var dt = new Date();
    document.getElementById('schedule-date').innerHTML = dt.toLocaleDateString();
});
// Function to fetch timeslot data from the backend
document.addEventListener('DOMContentLoaded', fetchTimeslotData);

async function fetchTimeslotData() {
    try {
        const response = await fetch('http://16.16.186.129/api/timeslot'); // Update with your backend URL if different
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
        const response = await fetch('http://16.16.186.129/api/api/teams-asking-for-match');
        const result = await response.json();

        if (result.success) {
            const teams = result.data;
            const teamList = document.getElementById('match-request-team-list');
            teamList.innerHTML = ''; // Clear any existing data

            teams.forEach(team => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `<strong>${team.Name}</strong> - ${team.Email}`;
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
        const response = await fetch('http://16.16.186.129/api/booking', {
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

document.addEventListener("DOMContentLoaded", () => {
    // Get the buttons
    const askForMatchButton = document.getElementById("ask-for-match-btn");
    const notAskForMatchButton = document.getElementById("not-ask-for-match-btn");

    // Add event listeners to the buttons
    askForMatchButton.addEventListener("click", async () => {
        const email = localStorage.getItem("loggedInEmail"); // Retrieve the logged-in user's email

        if (!email) {
            alert("You must be logged in to perform this action.");
            window.location.href = "login.html"; // Redirect to login page
            return;
        }

        try {
            const response = await fetch("http://16.16.186.129/api/ask-for-match", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email }),
            });

            const result = await response.json();

            if (response.ok) {
                alert("You are now looking for an opponent!");
            } else {
                alert(`Failed to update status: ${result.message || "Unknown error"}`);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred. Please try again later.");
        }
    });

    notAskForMatchButton.addEventListener("click", async () => {
        const email = localStorage.getItem("loggedInEmail"); // Retrieve the logged-in user's email

        if (!email) {
            alert("You must be logged in to perform this action.");
            window.location.href = "login.html"; // Redirect to login page
            return;
        }

        try {
            const response = await fetch("http://16.16.186.129/api/stop-asking-for-match", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email }),
            });

            const result = await response.json();

            if (response.ok) {
                alert("You are no longer looking for an opponent.");
            } else {
                alert(`Failed to update status: ${result.message || "Unknown error"}`);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred. Please try again later.");
        }
    });
});


document.addEventListener('DOMContentLoaded', fetchLeagueTableData);
async function fetchLeagueTableData() {
    const response = await fetch('http://16.16.186.129/api/rankings');
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
        const response = await fetch('http://16.16.186.129/api/api/teams');
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
        const response = await fetch(`http://16.16.186.129/api/api/teams/${teamId}`, {
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
        const response = await fetch(`http://16.16.186.129/api/api/teams/${teamId}`, {
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
        const response = await fetch('http://16.16.186.129/api/api/matches');
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
        const response = await fetch(`http://16.16.186.129/api/api/matches/${matchId}`, {
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
        const response = await fetch('http://16.16.186.129/api/api/timeslots');
        const result = await response.json();

        if (result.success) {
            const timeslotTableBody = document.getElementById('timeslot-management-table').getElementsByTagName('tbody')[0];
            timeslotTableBody.innerHTML = '';

            result.data.forEach(timeslot => {
                const row = document.createElement('tr');

                row.innerHTML = `
                    <td>${timeslot.Date}</td>
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
        const response = await fetch(`http://16.16.186.129/api/api/timeslots/${timeslotId}`, {
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

//Calendar Page
const daysTag = document.querySelector(".days"),
currentDate = document.querySelector(".current-date"),
prevNextIcon = document.querySelectorAll(".icons span");

// getting new date, current year and month
let date = new Date(),
currYear = date.getFullYear(),
currMonth = date.getMonth();

// storing full name of all months in array
const months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"];

const renderCalendar = () => {
    let firstDayofMonth = new Date(currYear, currMonth, 1).getDay(), // getting first day of month
    lastDateofMonth = new Date(currYear, currMonth + 1, 0).getDate(), // getting last date of month
    lastDayofMonth = new Date(currYear, currMonth, lastDateofMonth).getDay(), // getting last day of month
    lastDateofLastMonth = new Date(currYear, currMonth, 0).getDate(); // getting last date of previous month
    let liTag = "";

    for (let i = firstDayofMonth; i > 0; i--) { // creating li of previous month last days
        liTag += `<li class="inactive">${lastDateofLastMonth - i + 1}</li>`;
    }

    for (let i = 1; i <= lastDateofMonth; i++) { // creating li of all days of current month
        // adding active class to li if the current day, month, and year matched
        let isToday = i === date.getDate() && currMonth === new Date().getMonth() 
                     && currYear === new Date().getFullYear() ? "active" : "";
        liTag += `<li class="${isToday}">${i}</li>`;
    }

    for (let i = lastDayofMonth; i < 6; i++) { // creating li of next month first days
        liTag += `<li class="inactive">${i - lastDayofMonth + 1}</li>`
    }
    currentDate.innerText = `${months[currMonth]} ${currYear}`; // passing current mon and yr as currentDate text
    daysTag.innerHTML = liTag;
}
renderCalendar();

prevNextIcon.forEach(icon => { // getting prev and next icons
    icon.addEventListener("click", () => { // adding click event on both icons
        // if clicked icon is previous icon then decrement current month by 1 else increment it by 1
        currMonth = icon.id === "prev" ? currMonth - 1 : currMonth + 1;

        if(currMonth < 0 || currMonth > 11) { // if current month is less than 0 or greater than 11
            // creating a new date of current year & month and pass it as date value
            date = new Date(currYear, currMonth, new Date().getDate());
            currYear = date.getFullYear(); // updating current year with new date year
            currMonth = date.getMonth(); // updating current month with new date month
        } else {
            date = new Date(); // pass the current date as date value
        }
        renderCalendar(); // calling renderCalendar function
    });
});

//Calendar popup functions
document.addEventListener('DOMContentLoaded', () => {
    const daysContainer = document.querySelector('.days');
    const modal = document.getElementById('scheduler-popup');
    const closeModal = modal.querySelector('.scheduler-close');
    const popupDate = document.getElementById('scheduler-popup-date');
    const schedulerBody = document.getElementById('popup-scheduler-body');

    // Add click event listener to calendar days
    daysContainer.addEventListener('click', async (event) => {
        if (event.target.tagName === 'LI' && !event.target.classList.contains('inactive')) {
            const day = event.target.innerText;
            const date = `${currYear}-${String(currMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            
            // Set the popup title
            popupDate.innerText = date;

            // Fetch and populate scheduler data
            try {
                const response = await fetch(`http://16.16.186.129/api/timeslot-date?date=${date}`);
                const result = await response.json();

                if (result.success) {
                    populateSchedulerTable(result.data);
                } else {
                    console.error('Failed to fetch timeslot data:', result.error);
                }
            } catch (error) {
                console.error('Error fetching timeslot data:', error);
            }

            // Show the modal
            modal.style.display = 'flex';
        }
    });

    // Populate the scheduler table
    function populateSchedulerTable(data) {
        schedulerBody.innerHTML = '';
        data.forEach(slot => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${slot.StartTime} - ${slot.EndTime}</td>
                <td>${slot.Team1Name && slot.Team2Name ? `${slot.Team1Name} vs ${slot.Team2Name}` : 'Available'}</td>
                <td>${slot.IsBooked ? '<button class="booked" disabled>Booked</button>' : '<button class="book-now">Book Now</button>'}</td>
            `;
            schedulerBody.appendChild(row);
        });
    }

    // Close modal
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside content
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
