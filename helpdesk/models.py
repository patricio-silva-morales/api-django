from uuid import uuid4

from django.db import models


def nuevo_id():
    return uuid4().hex


class Ticket(models.Model):
    class Estado(models.TextChoices):
        ABIERTO = 'Abierto'
        EN_PROCESO = 'En proceso'
        CERRADO = 'Cerrado'

    class Prioridad(models.TextChoices):
        BAJA = 'Baja'
        MEDIA = 'Media'
        ALTA = 'Alta'

    id = models.CharField(primary_key=True, max_length=64, default=nuevo_id, editable=False)
    asunto = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=5000)
    estado = models.CharField(max_length=10, choices=Estado.choices, db_index=True)
    prioridad = models.CharField(max_length=5, choices=Prioridad.choices, db_index=True)
    fechaCreacion = models.DateField(db_index=True)

    class Meta:
        db_table = 'tickets'
        # AGREGADO: acelera el orden de la paginación.
        indexes = [
            models.Index(fields=['fechaCreacion', 'id'], name='tickets_fecha_id_idx'),
        ]


class Usuario(models.Model):
    class Rol(models.TextChoices):
        ADMINISTRADOR = 'Administrador'
        SOPORTE = 'Soporte'
        USUARIO = 'Usuario'

    id = models.CharField(primary_key=True, max_length=64, default=nuevo_id, editable=False)
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    rol = models.CharField(max_length=20, choices=Rol.choices)

    class Meta:
        db_table = 'usuarios'
