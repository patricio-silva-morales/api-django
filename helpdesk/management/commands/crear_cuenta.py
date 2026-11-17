from getpass import getpass

from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from helpdesk.models import Usuario


class Command(BaseCommand):
    help = 'Crea una cuenta de acceso con un perfil de la clase.'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('rol', choices=Usuario.Rol.values)

    def handle(self, *args, **opciones):
        username, rol = opciones['username'], opciones['rol']
        if User.objects.filter(username=username).exists():
            raise CommandError('Ya existe una cuenta con ese nombre.')
        password = getpass('Contraseña: ')
        if password != getpass('Repetir contraseña: '):
            raise CommandError('Las contraseñas no coinciden.')
        try:
            validate_password(password)
        except ValidationError as error:
            raise CommandError(' '.join(error.messages)) from error
        with transaction.atomic():
            user = User.objects.create_user(username=username, password=password)
            group, _ = Group.objects.get_or_create(name=rol)
            user.groups.add(group)
        self.stdout.write(self.style.SUCCESS(f'Cuenta {username} creada con rol {rol}.'))
