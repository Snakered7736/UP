/* ========= AUTH HEADER UI MANAGEMENT ========= */
function updateAuthUI() {
  const token = localStorage.getItem('token');
  const userName = localStorage.getItem('userName') || 'Профиль';

  const loginLink = document.querySelector('nav.main a[href="login.html"]');
  if (!loginLink) return;

  if (token) {
    // Пользователь авторизован - показать профиль и выход
    loginLink.parentElement.innerHTML = `
      <a href="profile.html" id="profileLink">${userName}</a>
      <a href="#" id="logoutLink" style="color: #ff8a00;">Выход</a>
    `;

    document.getElementById('logoutLink').addEventListener('click', (e) => {
      e.preventDefault();
      localStorage.clear();
      window.location.href = 'index.html';
    });
  }
}

document.addEventListener('DOMContentLoaded', updateAuthUI);
