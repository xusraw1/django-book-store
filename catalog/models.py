from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/default_avatar.png')
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_orders(self):
        return Order.objects.filter(user=self.user).order_by('-id')

class Catalog(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название каталога", null=True, blank=True)
    description = models.TextField(verbose_name="Описание каталога", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Каталог"
        verbose_name_plural = "Каталоги"

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название", null=True, blank=True)
    author = models.CharField(max_length=100, verbose_name="Автор", null=True, blank=True)
    description = models.TextField(verbose_name="Описание", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", null=True, blank=True)
    image = models.ImageField(upload_to='books/', verbose_name="Изображение", null=True, blank=True)
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE, verbose_name="Каталог", related_name='books', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.title} + {self.author}"

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

class Order(models.Model):
    DELIVERY_CHOICES = [
        ('BTS', 'BTS Express'),
        ('UZUM', 'Uzum Express'),
        ('UZPOST', 'Uzpost'),
        ('EMU', 'Emu Express'),
        ('OTHER', 'Другая служба'),
    ]

    PAYMENT_CHOICES = [
        ('UZCARD', 'UzCard'),
        ('HUMO', 'Humo'),
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('CASH', 'Наличные при получении'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Обрабатывается'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        null=True, blank=True
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    middle_name = models.CharField(max_length=50, verbose_name="Отчество")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    whatsapp = models.CharField(max_length=20, verbose_name="WhatsApp")
    email = models.EmailField(null=True, verbose_name="Email")
    address = models.TextField(null=True, verbose_name="Адрес")
    city = models.CharField(max_length=100, verbose_name="Город")
    region = models.CharField(max_length=100, verbose_name="Регион")
    postal_code = models.CharField(max_length=10, verbose_name="Почтовый индекс")
    delivery_method = models.CharField(max_length=15, choices=DELIVERY_CHOICES, verbose_name="Способ доставки")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, verbose_name="Способ оплаты")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"
    
    def get_items(self):
        return self.items.all()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} - {self.quantity} шт."