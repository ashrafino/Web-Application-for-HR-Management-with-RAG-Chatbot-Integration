// Initialize an array to hold the database entries
let database = [];

/**
 * Adds a new entry to the database and updates the table.
 */
function addEntry() {
    // Get values from input fields
    const name = document.getElementById('nameInput').value.trim();
    const email = document.getElementById('emailInput').value.trim();
    
    // Validate input
    if (name && email) {
        // Create a new entry object
        const newEntry = { name, email };
        database.push(newEntry);
        // Clear input fields
        document.getElementById('nameInput').value = '';
        document.getElementById('emailInput').value = '';
        // Render the updated table
        renderTable();
    } else {
        // Alert user if inputs are invalid
        alert('Please fill out both fields.');
    }
}

/**
 * Deletes an entry from the database by index and updates the table.
 * @param {number} index - The index of the entry to delete
 */
function deleteEntry(index) {
    // Remove the entry from the database
    database.splice(index, 1);
    // Render the updated table
    renderTable();
}

/**
 * Edits an existing entry in the database.
 * @param {number} index - The index of the entry to edit
 */
function editEntry(index) {
    // Prompt the user for new values
    const newName = prompt('Enter new name:', database[index].name);
    const newEmail = prompt('Enter new email:', database[index].email);

    // Validate new values
    if (newName && newEmail) {
        // Update the entry
        database[index] = { name: newName.trim(), email: newEmail.trim() };
        // Render the updated table
        renderTable();
    } else {
        // Alert user if new values are invalid
        alert('Both fields are required to update the entry.');
    }
}

/**
 * Renders the table with the current database entries.
 */
function renderTable() {
    // Get the table body element
    const tableBody = document.getElementById('databaseTable');
    tableBody.innerHTML = '';

    // Iterate over each entry in the database
    database.forEach((entry, index) => {
        // Create a new row
        const row = document.createElement('tr');

        // Create and append name cell
        const nameCell = document.createElement('td');
        nameCell.textContent = entry.name;
        row.appendChild(nameCell);

        // Create and append email cell
        const emailCell = document.createElement('td');
        emailCell.textContent = entry.email;
        row.appendChild(emailCell);

        // Create and append actions cell with edit and delete buttons
        const actionsCell = document.createElement('td');
        actionsCell.classList.add('actions');
        
        const editButton = document.createElement('button');
        editButton.classList.add('edit');
        editButton.textContent = 'Edit';
        editButton.onclick = () => editEntry(index);
        actionsCell.appendChild(editButton);
        
        const deleteButton = document.createElement('button');
        deleteButton.classList.add('delete');
        deleteButton.textContent = 'Delete';
        deleteButton.onclick = () => deleteEntry(index);
        actionsCell.appendChild(deleteButton);
        
        row.appendChild(actionsCell);
        tableBody.appendChild(row);
    });
}
