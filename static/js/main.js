/* 
 * Allow users to toggle password between astericks and original text.
 */
function togglePassword() {
    const passwordField = document.getElementById("password_input");
    if (passwordField) {
        if (passwordField.type === "password") {
            passwordField.type = "text";
        } else {
            passwordField.type = "password";
        }
    }
}

/*
 * The function would be triggered if a user clicks a post in the home route.
 * This redirects the user to the detailed view of a specific book.
 */
function viewDetails(bookId) {
    window.location.href = `/book/${bookId}`;
}

function togglePriceField() {
    const selector = document.getElementById('listing_type');
    const priceContainer = document.getElementById('price-container');
    const priceInput = document.getElementById('price');

    if (selector.value === 'Selling') {
        priceContainer.style.display = 'block';
        priceInput.setAttribute('required', 'true'); // Make price mandatory if selling
    } else {
        priceContainer.style.display = 'none';
        priceInput.removeAttribute('required');      // Not needed for lending
        priceInput.value = "";                       // Clear it if they switch back
    }
}

/*
 * Handles the "I want to borrow/buy" button click logic.
 * Communicates with the Flask backend to increment the interest count.
 */
async function handleLikeClick(event) {
    // Since this "like" button is in a book post, and "details of the book"
    // would be shown after a user clicks the post. This line ensures that the
    // click is handled by the "like" button instead of 
    event.stopPropagation(); 

    const button = event.currentTarget;
    const bookId = button.getAttribute('data-id');

    try {
        // Send the asynchronous request to flask to get all info of a book.
        const response = await fetch(`/like-book/${bookId}`, { 
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        
        const data = await response.json();

        if (!response.ok){
            alert(data.error); 
            
            // Gray out the button so they know they've already liked.
            // button.disabled = true;
            // button.innerText = "Forbidden to like!";
            return;
        }
        if (data.action == "like"){
            button.innerText = "Liked!"
            button.classList.add('liked'); // can style this later in css
        }
        else{
            button.innerText = "Unliked!";
            button.classList.add('unliked'); // same as above.
        }

        // Update the like count if the backend returned a new count
        if (data.new_count !== undefined) {
            const post = button.closest('.book-post');
            const countDisplay = post.querySelector('.interest-count');
            if (countDisplay) {
                countDisplay.innerText = data.new_count;
            }
        }
    } catch (err) {
        console.error('Error updating interest count:', err);
    }
}

// You can think of the document object as the JavaScript representation of the current page.
document.addEventListener("DOMContentLoaded", () => {
    togglePriceField();
    const likeButtons = document.querySelectorAll('.like-btn')

    likeButtons.forEach(button => {
        button.addEventListener('click', handleLikeClick);
    });
})