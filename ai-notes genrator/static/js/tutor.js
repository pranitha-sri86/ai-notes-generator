const form = document.querySelector("form");
const loadingBox = document.getElementById("loadingBox");
const chatBox = document.getElementById("chatBox");

// SHOW LOADER

form.addEventListener("submit", () => {

loadingBox.classList.remove("d-none");


});

// AUTO SCROLL

window.onload = () => {

chatBox.scrollTop = chatBox.scrollHeight;


};

// ENTER TO SEND

document.querySelector("textarea")
.addEventListener("keydown", function(e){


if(e.key === "Enter" && !e.shiftKey){

    e.preventDefault();

    form.submit();

}

});
