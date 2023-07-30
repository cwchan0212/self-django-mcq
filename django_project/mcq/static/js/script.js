function toggleOptions(optionType) {
    if (optionType === "radio") {
        for (let i = 1; i < 3; i++) {
            document.getElementById("radioOptions" + i).style.display = "table-row";
        }
        for (let i = 1; i < 9; i++) {
            document.getElementById("checkboxOptions" + i).style.display = "none";
        }
    } else if (optionType === "checkbox") {
        for (let i = 1; i < 3; i++) {
            document.getElementById("radioOptions" + i).style.display = "none";
        }
        for (let i = 1; i < 9; i++) {
            document.getElementById("checkboxOptions" + i).style.display = "table-row";
        }
    }
}
// ------------------------------------------------------------------------------------------------
function goReset() {
    window.location.href = "/data/question/new";
}
// ------------------------------------------------------------------------------------------------
function sectionChange() {
    section_change_form = document.getElementById("quiz_section_change");
    section_change_form.submit();
}
