from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers

from recipes.views import TagViewSet, RecipeViewSet, FavoriteViewSet, ShoppingListViewSet, GetRecipeShortLink, IngredientViewSet
# from ingredients.views import IngredientViewSet
from users.views import UserAvatarViewSet, FollowViewSet, SubscribeViewSet, UsersMeViewSet

# router = routers.DefaultRouter()
# router.register(r'tags', TagViewSet)
# router.register(r'ingredients', IngredientViewSet)
# router.register(r'recipes', RecipeViewSet)
# router.register(r'users/subscriptions', FollowViewSet, basename='follows')
# router.register(r'users/me', UsersMeViewSet, basename='usersme')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('redoc/', TemplateView.as_view(template_name='redoc.html'), name='redoc'
         ),
    # path('api/recipes/shopping_cart/', ShoppingListViewSet.as_view()),
    # path('api/recipes/<int:id>/shopping_cart/', ShoppingListViewSet.as_view()),
    
    # path('api/recipes/<int:id>/favorite/', FavoriteViewSet.as_view()),
    # path('api/users/<int:id>/subscribe/', SubscribeViewSet.as_view()),
    # path('api/recipes/<int:id>/s/<slug:short_url>', GetRecipe.as_view()),
    # path('api/users/me/', UsersMeViewSet),
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
    # path('api/', include(router.urls)),
    # path('api/', include('djoser.urls')),
    # path('api/auth/', include('djoser.urls.authtoken')),

    path('s/<slug:short_url>/', GetRecipeShortLink.as_view()),
    # path('api/users/me/avatar/', UserAvatarViewSet.as_view()),
    
]
