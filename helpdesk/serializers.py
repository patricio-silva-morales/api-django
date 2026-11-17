from rest_framework import serializers

from .models import Ticket, Usuario


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id', 'asunto', 'descripcion', 'estado', 'prioridad', 'fechaCreacion')
        read_only_fields = ('id',)


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'nombre', 'email', 'rol')
        read_only_fields = ('id',)
