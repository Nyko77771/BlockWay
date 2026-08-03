document.addEventListener("DOMContentLoaded", () => {

    const toggleCheckbox = document.getElementsByClassName("toggle_checkbox");
    const passwordInputs = document.querySelectorAll(".password");

    toggleCheckbox[0].addEventListener(
        "change", function () {
            passwordInputs.forEach((passwordInput) => {
                if (this.checked) {
                    passwordInput.type = "text"
                } else {
                    passwordInput.type = "password"
                }
            } 
        )
        }
    );
});