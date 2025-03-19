# catalog/context_processors.py
from .models import Catalog

def catalogs(request):
    return {'catalogs': Catalog.objects.all()}


def cart_item_count(request):
    cart = request.session.get('cart', {})
    unique_items_count = len(cart)  # Количество уникальных товаров
    return {'cart_item_count': unique_items_count}
