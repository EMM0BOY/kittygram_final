from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__email', 'author__username')
    inlines = (RecipeIngredientInline,)

    def favorites_count(self, obj):
        return obj.favorited_by.count()
    favorites_count.short_description = 'Добавлений в избранное'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__email', 'recipe__name')

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__email', 'recipe__name')