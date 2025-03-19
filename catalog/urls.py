from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),  # Главная страница
    path('about/', views.about, name='about'),  # Страница "О нас"
    path('catalog/<int:catalog_id>/', views.book_list, name='book_list_by_catalog'),  # Книги по каталогу
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),  # Детальная страница книги
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),  # Добавление в корзину
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:book_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('register/', views.register, name='register'),  # Регистрация
    path('login/', views.user_login, name='login'),  # Вход
    path('logout/', views.user_logout, name='logout'),  # Выход
    path('checkout/', views.checkout, name='checkout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]