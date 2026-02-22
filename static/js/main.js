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
        
        if (!response.ok){
            const errorData = await response.json();
            alert(errorData.error); 
            
            // Gray out the button so they know they've already liked.
            button.disabled = true;
            button.innerText = "Forbidden to like!";
            return;
        }

        const data = await response.json();

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

document.addEventListener("DOMContentLoaded", () => {
    const likeButtons = document.querySelectorAll('.like-btn')
    likeButtons.forEach(button => {
        button.addEventListener('click', handleLikeClick);
    });
})