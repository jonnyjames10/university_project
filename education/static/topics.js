// var notes = document.getElementById("notes").addEventListener("click", displayNotes);
// var video = document.getElementById("video").addEventListener("click", displayVideo);
// var game = document.getElementById("game").addEventListener("click", displayGame);
// var test = document.getElementById("test").addEventListener("click", displayTest);

let button = document.querySelectorAll('.topic_navbar button');
let content_inside = document.querySelectorAll('.content_inside');

Array.from(button).forEach(function(buttonArray, i) {
    buttonArray.addEventListener('click', function() {

        Array.from(button).forEach(buttonAll => buttonAll.classList.remove('button_active'));
        
        Array.from(content_inside).forEach(content_insideAll => content_insideAll.classList.remove('content_inside_active'));
        
        button[i].classList.add('button_active'); 
        
        content_inside[i].classList.add('content_inside_active');  
    });
});