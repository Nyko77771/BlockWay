document.addEventListener('DOMContentLoaded', () => {
    const option1 = document.getElementById("option1");
    const option2 = document.getElementById("option2");
    const autoSelection = document.querySelector(".pihole_auto_selection");
    const manualSelection = document.querySelector(".pihole_manual_select");

    option1.addEventListener("change", function () {
        if (this.checked) {
        autoSelection.hidden = false;
        manualSelection.hidden = true;
        }
    });
    option2.addEventListener("change", function () {
        if (this.checked) {
        autoSelection.hidden = true;
        manualSelection.hidden = false;
        }
    });

})