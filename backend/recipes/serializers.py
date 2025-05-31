import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import UserSerializer
from users.serializers import CustomUserSerializer
from .models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4().hex[:10]
            data = ContentFile(base64.b64decode(imgstr), name=f"{id}.{ext}")
        return super().to_internal_value(data)

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'ingredients',
            'cooking_time', 'is_favorited', 'is_in_shopping_cart', 'favorites_count'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.favorited_by.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.in_carts.filter(user=user).exists()

    def get_favorites_count(self, obj):
        return obj.favorited_by.count()

class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'text', 'ingredients', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user, **validated_data)
        for item in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            for item in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient_id=item['id'],
                    amount=item['amount']
                )
        return super().update(instance, validated_data)