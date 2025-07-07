document.addEventListener("DOMContentLoaded", () => {
  const dropdowns = document.querySelectorAll('.teacher-dropdown .dropdown');

  dropdowns.forEach(drop => {
    const button = drop.querySelector('.dropbtn');
    const menu = drop.querySelector('.dropdown-content');

    if (button && menu) {
      button.addEventListener('click', e => {
        e.stopPropagation();
        menu.classList.toggle('active');
      });

      document.addEventListener('click', () => {
        menu.classList.remove('active');
      });
    }
  });
});
