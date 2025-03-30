from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
import random


"""
Все функции связанные с профилем
"""

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    delivery_display = order.get_delivery_method_display()
    payment_display = order.get_payment_method_display()

    return render(request, 'catalog/profile_orders.html', {
        'order': order,
        'delivery_display': delivery_display,
        'payment_display': payment_display
    })

@login_required
def profile_view(request):
    return render(request, 'catalog/profile.html', {'profile': request.user.profile})

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)  # Добавил request.FILES!
        if form.is_valid():
            form.save()
            messages.info(request, "Профиль успешно изменен!")
            return redirect('profile')  # После сохранения вернемся в профиль
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'catalog/edit_profile.html', {'form': form})


def checkout(request):
    cart = request.session.get('cart', {})
    
    # Если корзина пустая, перенаправляем на страницу с корзиной
    if not cart:
        return redirect('cart')

    # Обновляем цену в корзине
    for book_id, item in cart.items():
        item['item_total'] = round(float(item['price']) * int(item['quantity']), 2)
    request.session['cart'] = cart

    # Общая стоимость заказа
    total_price = sum(item['item_total'] for item in cart.values())

    if request.method == "POST":
        order_form = OrderForm(request.POST)
        delivery_form = DeliveryPaymentForm(request.POST)

        if 'personal_info' in request.POST:
            if order_form.is_valid():
                request.session['order_data'] = order_form.cleaned_data
                return redirect('checkout')  # Переходим ко второму шагу

        elif 'delivery_payment' in request.POST:
            if delivery_form.is_valid():
                order_data = request.session.get('order_data', {})
                if not order_data:
                    return redirect('checkout')

                # Добавляем способ доставки и оплаты в order_data
                order_data['delivery_method'] = delivery_form.cleaned_data['delivery_method']
                order_data['payment_method'] = delivery_form.cleaned_data['payment_method']

                order = Order.objects.create(**order_data, user=request.user, total_price=total_price)

                # Проходим по товарам в корзине и создаем OrderItem
                for book_id, item in cart.items():
                    book = Book.objects.get(id=book_id)  # Получаем книгу по ID
                    OrderItem.objects.create(
                        order=order,
                        book=book,  # Сохраняем объект книги
                        quantity=item['quantity'],
                        price=item['price']
                    )

                # Очищаем сессию после оформления заказа
                del request.session['cart']
                del request.session['order_data']
                
                return redirect('order_success', order_id=order.id)

    else:
        order_form = OrderForm(initial=request.session.get('order_data', {}))
        delivery_form = DeliveryPaymentForm()

    return render(request, 'catalog/checkout.html', {
        'order_form': order_form,
        'delivery_form': delivery_form,
        'cart': cart,
        'total_price': total_price,
    })

def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    total_price = sum(item.price * item.quantity for item in order_items)

    # Используем встроенные методы Django для получения текстовых значений
    delivery_method_display = order.get_delivery_method_display() if order.delivery_method else "Неизвестно"
    payment_method_display = order.get_payment_method_display() if order.payment_method else "Неизвестно"

    return render(request, 'catalog/order_success.html', {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'delivery_method_display': delivery_method_display,
        'payment_method_display': payment_method_display,
    })

"""Регистрация нового пользователя"""
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = RegisterForm()
    return render(request, 'catalog/register.html', {'form': form})


"""Вход в аккаунт"""
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('book_list')  # Перенаправляем на главную страницу
    else:
        form = LoginForm()
    return render(request, 'catalog/login.html', {'form': form})


"""Выход из профиля"""
@login_required
def user_logout(request):
    logout(request)
    return redirect('book_list')  # Перенаправляем на главную страницу

"""Функции связанные с оформлением заказов"""
def cart_view(request):
    cart = request.session.get('cart', {})
    
    cart_items = {}
    total = 0  # Общая сумма корзины

    for book_id, item in cart.items():
        price = float(item['price'])  # Убедимся, что цена в float
        quantity = int(item['quantity'])
        item_total = round(price * quantity, 2)  # Цена * Количество
        
        cart_items[book_id] = {
            'title': item['title'],
            'price': price,
            'quantity': quantity,
            'item_total': item_total  # Считаем сумму одной позиции
        }
        
        total += item_total  # Подсчёт общей суммы
    
    # Получаем все книги, если они есть
    all_books = list(Book.objects.all())  
    random_books = random.sample(all_books, min(4, len(all_books))) if all_books else []  # Проверка на пустой список

    return render(request, 'catalog/cart.html', {
        'cart': cart_items,
        'total': total,
        'random_books': random_books
    })

def calculate_total(cart):
    """Функция для пересчета общей стоимости"""
    return sum(int(item["quantity"]) * float(item["price"]) for item in cart.values())


def update_cart(request, book_id, action):
    cart = request.session.get("cart", {})

    if str(book_id) in cart:
        if action == "increase":
            cart[str(book_id)]["quantity"] += 1
        elif action == "decrease":
            if cart[str(book_id)]["quantity"] > 1:
                cart[str(book_id)]["quantity"] -= 1
            else:
                del cart[str(book_id)]  # Если 0 товаров, удаляем из корзины

    request.session["cart"] = cart
    request.session.modified = True

    return redirect(reverse("cart"))  # Перенаправляем обратно в корзину

def remove_from_cart(request, book_id):
    cart = request.session.get("cart", {})
    
    if str(book_id) in cart:
        del cart[str(book_id)]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect(reverse("cart"))


def add_to_cart(request, book_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Войдите в систему, чтобы добавить книгу в корзину.")
        return redirect('/login/?next=' + request.path)  # После входа вернет обратно

    # Если пользователь авторизован — продолжаем обычное добавление
    book = get_object_or_404(Book, id=book_id)
    cart = request.session.get('cart', {})

    if str(book_id) in cart:
        cart[str(book_id)]['quantity'] += 1
        messages.success(request, f'Вы добавили ещё один экземпляр "{book.title}" в корзину.')
    else:
        cart[str(book_id)] = {'title': book.title, 'price': str(book.price), 'quantity': 1}
        messages.success(request, f'Книга "{book.title}" добавлена в корзину!')

    request.session['cart'] = cart
    return redirect('cart')




"""Главная страница и просмотр книг"""
def book_list(request, catalog_id=None):
    query = request.GET.get('q', '')  # Получаем параметр 'q' из запроса
    books_list = Book.objects.all()  # Базовый queryset

    if catalog_id:
        catalog = get_object_or_404(Catalog, id=catalog_id)
        books_list = catalog.books.all()  # Фильтруем по каталогу

    # Фильтрация по названию или автору, если введён запрос
    if query:
        books_list = books_list.filter(title__icontains=query) | books_list.filter(author__icontains=query)

    paginator = Paginator(books_list, 3)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    catalogs = Catalog.objects.all()

    return render(request, 'catalog/book_list.html', {'books': books, 'catalogs': catalogs, 'query': query})

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Получаем книги из той же категории, исключая текущую
    related_books = Book.objects.filter(catalog=book.catalog).exclude(id=book.id)[:4]

    return render(request, 'catalog/book_detail.html', {
        'book': book,
        'related_books': related_books
    })

def about(request):
    return render(request, 'catalog/about.html')