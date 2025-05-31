from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Sum
from django.http import HttpResponse
from .models import Recipe, Ingredient
from .serializers import (
    RecipeReadSerializer,
    RecipeWriteSerializer,
    IngredientSerializer,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ["name"]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(
        detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == "POST":
            recipe.favorited_by.get_or_create(user=user)
            return Response(status=status.HTTP_201_CREATED)
        recipe.favorited_by.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == "POST":
            recipe.in_carts.get_or_create(user=user)
            return Response(status=status.HTTP_201_CREATED)
        recipe.in_carts.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            Recipe.objects.filter(in_carts__user=user)
            .values(
                "recipe_ingredients__ingredient__name",
                "recipe_ingredients__ingredient__measurement_unit",
            )
            .annotate(total=Sum("recipe_ingredients__amount"))
        )
        lines = [
            f"{item['recipe_ingredients__ingredient__name']} - {item['total']} {item['recipe_ingredients__ingredient__measurement_unit']}"
            for item in ingredients
        ]
        content = "".join(lines)
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="shopping_list.txt"'
        return response
