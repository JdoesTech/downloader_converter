function toggleNavBar() {
    const nav =document.querySelector('nav');
    const main = document.querySelector('main');

    nav.classList.toggle('collapsed');
    main.classList.toggle('shifted');
}