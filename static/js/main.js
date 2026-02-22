/* Allow users to toggle password between astericks and original text.
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