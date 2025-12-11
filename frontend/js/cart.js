/* ========= CART FUNCTIONALITY ========= */
class Cart {
  constructor() {
    this.items = JSON.parse(localStorage.getItem('cart') || '[]');
    this.updateBadge();
    this.initDropdown();
  }

  addItem(product) {
    const existing = this.items.find(item => item.id === product.id);
    if (existing) {
      existing.quantity++;
    } else {
      this.items.push({ ...product, quantity: 1 });
    }
    this.save();
    this.updateBadge();
    this.renderDropdown();
  }

  removeItem(id) {
    this.items = this.items.filter(item => item.id !== id);
    this.save();
    this.updateBadge();
    this.renderDropdown();
  }

  updateQuantity(id, delta) {
    const item = this.items.find(item => item.id === id);
    if (item) {
      item.quantity += delta;
      if (item.quantity <= 0) {
        this.removeItem(id);
      } else {
        this.save();
        this.renderDropdown();
      }
    }
  }

  getTotalCount() {
    return this.items.reduce((sum, item) => sum + item.quantity, 0);
  }

  getTotalPrice() {
    return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  }

  save() {
    localStorage.setItem('cart', JSON.stringify(this.items));
  }

  updateBadge() {
    const badge = document.getElementById('cartBadge');
    const count = this.getTotalCount();
    badge.textContent = count;
    badge.classList.toggle('hidden', count === 0);
  }

  renderDropdown() {
    const container = document.getElementById('cartItemsContainer');
    const footer = document.getElementById('cartFooter');

    if (this.items.length === 0) {
      container.innerHTML = '<div class="cart-empty">Корзина пуста</div>';
      footer.style.display = 'none';
      return;
    }

    container.innerHTML = this.items.map(item => {
      // Определяем, нужны ли кавычки для ID (строки vs числа)
      const idIsString = typeof item.id === 'string';
      const idParam = idIsString ? `'${item.id}'` : item.id;

      return `
      <div class="cart-item">
        <img src="${item.image}" alt="${item.name}" class="cart-item-image" onerror="this.src='images/1.png'">
        <div class="cart-item-details">
          <div class="cart-item-name">${item.name}</div>
          <div class="cart-item-price">${item.price} ₽</div>
          <div class="cart-item-controls">
            <button class="cart-item-btn" onclick="cart.updateQuantity(${idParam}, -1)">−</button>
            <span class="cart-item-quantity">${item.quantity}</span>
            <button class="cart-item-btn" onclick="cart.updateQuantity(${idParam}, 1)">+</button>
            <button class="cart-item-remove" onclick="cart.removeItem(${idParam})">Удалить</button>
          </div>
        </div>
      </div>
      `;
    }).join('');

    document.getElementById('cartTotal').textContent = `${this.getTotalPrice()} ₽`;
    footer.style.display = 'block';
  }

  initDropdown() {
    const icon = document.getElementById('cartIcon');
    const dropdown = document.getElementById('cartDropdown');

    if (!icon || !dropdown) {
      console.warn('Cart elements not found');
      return;
    }

    icon.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      dropdown.classList.toggle('show');
      this.renderDropdown();
    });

    // Остановить всплытие событий внутри dropdown
    dropdown.addEventListener('click', (e) => {
      e.stopPropagation();
    });

    document.addEventListener('click', (e) => {
      if (!dropdown.contains(e.target) && !icon.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });
  }
}

// Создаем глобальный объект корзины
const cart = new Cart();
window.cart = cart;
