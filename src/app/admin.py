from django.contrib import admin
from .models import Dota2Item, Dota2ItemImage


class Dota2ItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'market_hash_name', 'class_name')
    search_fields = ('market_hash_name', )


admin.site.register(Dota2Item, Dota2ItemAdmin)
admin.site.register(Dota2ItemImage)
