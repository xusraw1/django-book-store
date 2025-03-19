from django.contrib import admin
from .models import Book, Catalog, Order

admin.site.register(Book)
admin.site.register(Catalog)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at', 'total_price')
    list_filter = ('status',)
    search_fields = ('id',)