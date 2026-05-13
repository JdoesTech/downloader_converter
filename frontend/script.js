function toggleNavBar() {
    const header = document.querySelector('header');
    const nav =document.querySelector('nav');
    const main = document.querySelector('main');

    header.classList.toggle('shifted');
    nav.classList.toggle('collapsed');
    main.classList.toggle('shifted');
}

document.addEventListener("DOMContentLoaded", ()=>{
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "true") {
        document.body.classList.add('dark-mode');
    }
})

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem("theme", document.body.classList.contains('dark-mode'));
}

function login(){
    const username= document.getElementById("username").value;
    const password= document.getElementById("password").value;
    const message = document.getElementById("message");

    if(username){
        message.style.color = "green";
        message.textContent = "Login successful"
    }
    else {
        message.style.color = "red";
        message.textContent = "Invalid email or password"
    }
}