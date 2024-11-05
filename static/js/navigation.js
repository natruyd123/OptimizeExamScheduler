document.getElementById('brand-link').addEventListener('click', function (event) {
    event.preventDefault(); // Prevent the default link behavior
    window.location.href = 'index.html'; // Redirect to index.html
});

document.addEventListener('DOMContentLoaded', function () {
    const profileBtn = document.getElementById('profileBtn');
    const profileInfo = document.getElementById('profile-info');
    const logoutBtn = document.getElementById('logout-btn');

    logoutBtn.addEventListener('click', () => {
        window.location.href = "/logout";
    });

    // Toggle profile info on button click
    profileBtn.addEventListener('click', (event) => {
        event.stopPropagation(); // Prevent the click from propagating to the document
        profileInfo.style.display = (profileInfo.style.display === 'block') ? 'none' : 'block';
    });

    //Hide profile info when clicking outside
    document.addEventListener('click', (event) => {
        if (!profileInfo.contains(event.target) && !profileBtn.contains(event.target)) {
            profileInfo.style.display = 'none';
        }
    });

    const table = document.getElementById('editableTable');
    const generateSchedBtn = document.getElementById('generateSchedBtn');


    // Navigate to history.html on "Generate Schedule" button click
    generateSchedBtn.addEventListener('click', function () {
        // const url = this.getAttribute('data-url');
        // window.location.href = url;
        showProgressCard();
        setTimeout(() => {
            window.location.href = '/history';
        }, 2000);
    });

    // Function to show progress card
    function showProgressCard() {
        overlay.style.display = 'block'; // Show the overlay
        progressCard.style.display = 'block'; //show the progresscard
        simulateProgressCard();
    }

    // Function to simulate progress
    function simulateProgressCard() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            if (progress >= 100) {
                clearInterval(interval);
            } else {
                return simulateProgressCard();
            }
        }, 500);
    }

    if (table) {
        // Make table cells editable
        table.querySelectorAll('td').forEach(cell => {
            cell.contentEditable = true;
            cell.classList.add('editable');
        });
    }

    // Add new row
    document.getElementById('addRow').addEventListener('click', function () {
        const newRow = table.insertRow();
        for (let i = 0; i < table.rows[0].cells.length; i++) {
            const newCell = newRow.insertCell();
            newCell.contentEditable = true;
            newCell.classList.add('editable');
        }
    });

    // Add new column
    document.getElementById('addColumn').addEventListener('click', function () {
        const headerRow = table.rows[0];
        const newHeaderCell = document.createElement('th');
        newHeaderCell.contentEditable = true;
        newHeaderCell.classList.add('editable');
        headerRow.appendChild(newHeaderCell);

        for (let i = 1; i < table.rows.length; i++) {
            const newCell = table.rows[i].insertCell();
            newCell.contentEditable = true;
            newCell.classList.add('editable');
        }
    });
});