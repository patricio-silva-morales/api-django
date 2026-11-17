from django.urls import include, path
from rest_framework.routers import SimpleRouter

from helpdesk.views import Login, TicketViewSet, UsuarioViewSet

# Las rutas mantienen el formato de JSON Server sin barra al final.
router = SimpleRouter(trailing_slash=False)
router.register('tickets', TicketViewSet, basename='tickets')
router.register('usuarios', UsuarioViewSet, basename='usuarios')
router.register('usuario', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('auth/token', Login.as_view()),
    path('', include(router.urls)),
]
