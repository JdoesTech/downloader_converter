function toggleNavBar() {
    const header = document.querySelector('header');
    const nav =document.querySelector('nav');
    const main = document.querySelector('main');

    header.classList.toggle('shifted');
    nav.classList.toggle('collapsed');
    main.classList.toggle('shifted');
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem("theme", document.body.classList.contains('dark-mode'));
}