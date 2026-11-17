import json
from datetime import date, timedelta
from random import Random

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from helpdesk.models import Ticket, Usuario


class Command(BaseCommand):
    help = 'Importa registros de la clase y completa una muestra sintética reproducible.'

    def add_arguments(self, parser):
        parser.add_argument('--tickets', type=int, default=10000)
        parser.add_argument('--usuarios', type=int, default=1000)

    def handle(self, *args, **opciones):
        base = json.loads((settings.BASE_DIR / 'datos' / 'base.json').read_text(encoding='utf-8'))
        cantidad_tickets = opciones['tickets'] - len(base['tickets'])
        cantidad_usuarios = opciones['usuarios'] - len(base['usuarios'])
        if min(cantidad_tickets, cantidad_usuarios) < 0:
            raise CommandError('Las cantidades deben cubrir al menos los registros de base.json.')

        azar = Random(15)
        tickets = [Ticket(**fila) for fila in base['tickets']]
        usuarios = [Usuario(**fila) for fila in base['usuarios']]
        temas = [
            'Error de acceso a la VPN', 'Solicitud de permisos', 'Impresora sin conexión',
            'Problema con correo', 'Equipo lento', 'Actualización de software',
        ]
        for i in range(1, cantidad_tickets + 1):
            tema = azar.choice(temas)
            tickets.append(Ticket(
                id=f'demo-t-{i}', asunto=f'{tema} · Caso {i}',
                descripcion=f'Caso de práctica {i}. Solicitud de soporte: {tema}.',
                estado=azar.choices(Ticket.Estado.values, weights=[40, 35, 25])[0],
                prioridad=azar.choices(Ticket.Prioridad.values, weights=[25, 45, 30])[0],
                fechaCreacion=date(2026, 8, 1) + timedelta(days=azar.randrange(108)),
            ))

        for i in range(1, cantidad_usuarios + 1):
            usuarios.append(Usuario(
                id=f'demo-u-{i}', nombre=f'Usuario ficticio {i:04}',
                email=f'usuario{i}@example.test', rol=Usuario.Rol.USUARIO,
            ))

        # Las claves estables permiten repetir la carga sin duplicar registros.
        with transaction.atomic():
            Ticket.objects.bulk_create(tickets, batch_size=500, ignore_conflicts=True)
            Usuario.objects.bulk_create(usuarios, batch_size=500, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(
            f'SQLite: {Ticket.objects.count()} tickets y {Usuario.objects.count()} usuarios.'
        ))
