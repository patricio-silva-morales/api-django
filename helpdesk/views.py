from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import filters, permissions, serializers, status, throttling, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Ticket, Usuario
from .serializers import TicketSerializer, UsuarioSerializer


class Login(ObtainAuthToken):
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        cuenta = serializer.validated_data['user']
        grupos = set(cuenta.groups.values_list('name', flat=True))

        if cuenta.is_superuser or Usuario.Rol.ADMINISTRADOR in grupos:
            rol = Usuario.Rol.ADMINISTRADOR
        elif Usuario.Rol.SOPORTE in grupos:
            rol = Usuario.Rol.SOPORTE
        elif Usuario.Rol.USUARIO in grupos:
            rol = Usuario.Rol.USUARIO
        else:
            return Response(
                {'detail': 'La cuenta no tiene un rol asignado en el Help Desk.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        token, _ = Token.objects.get_or_create(user=cuenta)

        return Response({
            'token': token.key,
            'rol': rol,
            'username': cuenta.get_username(),
        })


class PermisoHelpDesk(permissions.BasePermission):
    def has_permission(self, request, view):
        if settings.MODO_LOCAL_ABIERTO:
            return True

        usuario = request.user
        if not usuario.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS or usuario.is_superuser:
            return True

        grupos = [Usuario.Rol.ADMINISTRADOR]

        if view.basename == 'tickets' and request.method != 'DELETE':
            grupos.append(Usuario.Rol.SOPORTE)

        return usuario.groups.filter(name__in=grupos).exists()


class RecursoHelpDesk(viewsets.ModelViewSet):
    permission_classes = [PermisoHelpDesk]

    def get_authenticators(self):
        if settings.MODO_LOCAL_ABIERTO:
            return []

        return super().get_authenticators()


# AGREGADO: configura el tamaño de página.
class PaginacionTickets(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# AGREGADO: valida los filtros que envía Angular.
class FiltrosTickets(serializers.Serializer):
    texto = serializers.CharField(required=False, allow_blank=True, max_length=200)
    estado = serializers.ChoiceField(choices=Ticket.Estado.choices, required=False)
    prioridad = serializers.ChoiceField(choices=Ticket.Prioridad.choices, required=False)
    fechaDesde = serializers.DateField(required=False)
    fechaHasta = serializers.DateField(required=False)

    def validate(self, datos):
        desde = datos.get('fechaDesde')
        hasta = datos.get('fechaHasta')

        if desde and hasta and desde > hasta:
            raise serializers.ValidationError({
                'fechaHasta': 'Debe ser igual o posterior a Desde.'
            })

        return datos


class TicketViewSet(RecursoHelpDesk):
    queryset = Ticket.objects.order_by('fechaCreacion', 'id')
    serializer_class = TicketSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['asunto', 'descripcion']
    ordering_fields = ['fechaCreacion', 'prioridad', 'estado', 'asunto']

    def get_queryset(self):
        tickets = super().get_queryset()

        for campo in ('estado', 'prioridad', 'fechaCreacion'):
            valor = self.request.query_params.get(campo)

            if not valor:
                continue

            if campo == 'fechaCreacion':
                try:
                    tickets = tickets.filter(fechaCreacion=valor)
                except DjangoValidationError as error:
                    raise ValidationError(
                        {'fechaCreacion': 'Usa AAAA-MM-DD.'}
                    ) from error
            else:
                tickets = tickets.filter(**{campo: valor})

        return tickets

    # AGREGADO: filtra en SQLite y devuelve una página.
    @action(detail=False, methods=['get'], pagination_class=PaginacionTickets)
    def paginados(self, request):
        filtros = FiltrosTickets(data=request.query_params)
        filtros.is_valid(raise_exception=True)
        datos = filtros.validated_data

        tickets = self.get_queryset()
        texto = datos.get('texto')

        if texto:
            tickets = tickets.filter(
                Q(id__icontains=texto)
                | Q(asunto__icontains=texto)
                | Q(descripcion__icontains=texto)
                | Q(estado__icontains=texto)
                | Q(prioridad__icontains=texto)
            )

        if 'fechaDesde' in datos:
            tickets = tickets.filter(fechaCreacion__gte=datos['fechaDesde'])

        if 'fechaHasta' in datos:
            tickets = tickets.filter(fechaCreacion__lte=datos['fechaHasta'])

        pagina = self.paginate_queryset(tickets)
        resultados = self.get_serializer(pagina, many=True).data
        return self.get_paginated_response(resultados)


class UsuarioViewSet(RecursoHelpDesk):
    queryset = Usuario.objects.order_by('nombre', 'id')
    serializer_class = UsuarioSerializer