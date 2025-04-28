// Function to handle the Add Publication button click
document.addEventListener('DOMContentLoaded', function() {
    const addPubBtn = document.createElement('button');
    addPubBtn.id = 'add-pub-btn';
    addPubBtn.textContent = 'Add Publication';
    document.querySelector('main').prepend(addPubBtn);

    // Create form HTML
    const formHTML = `
        <div id="form-overlay">
            <div id="pub-form-container">
                <form id="pub-form">
                    <h2>Add New Publication</h2>
                    <label for="pub-title">Title:</label>
                    <input type="text" id="pub-title" required>
                    
                    <label for="pub-author">Author:</label>
                    <input type="text" id="pub-author" required>
                    
                    <label for="pub-description">Description:</label>
                    <textarea id="pub-description" rows="6" required></textarea>
                    
                    <label for="pub-image">Image:</label>
                    <input type="file" id="pub-image" accept="image/*">

                    <div class="form-buttons">
                        <button type="submit">Submit</button>
                        <button type="button" id="cancel-btn">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    `;

    // Add form to body (hidden by default)
    document.body.insertAdjacentHTML('beforeend', formHTML);
    document.getElementById('form-overlay').style.display = 'none';

    // Event listeners
    addPubBtn.addEventListener('click', showForm);
    document.getElementById('cancel-btn').addEventListener('click', hideForm);
    document.getElementById('pub-form').addEventListener('submit', handleSubmit);

    function showForm() {
        document.getElementById('form-overlay').style.display = 'flex';
        document.body.classList.add('blur-effect');
    }

    function hideForm() {
        document.getElementById('form-overlay').style.display = 'none';
        document.body.classList.remove('blur-effect');
    }

    function handleSubmit(e) {
        e.preventDefault();
        // Here you would normally handle form submission
        alert('Publication submitted!');
        hideForm();
    }
});
