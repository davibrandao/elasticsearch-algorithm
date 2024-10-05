from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'