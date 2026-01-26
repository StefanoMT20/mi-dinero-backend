from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.categories.signals import create_default_categories_for_user

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea categorías por defecto para todos los usuarios existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Email del usuario específico (opcional)',
        )

    def handle(self, *args, **options):
        user_email = options.get('user')

        if user_email:
            try:
                user = User.objects.get(email=user_email)
                users = [user]
            except User.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f'Usuario con email "{user_email}" no encontrado')
                )
                return
        else:
            users = User.objects.all()

        total_created = 0
        users_updated = 0

        for user in users:
            created = create_default_categories_for_user(user)
            if created > 0:
                total_created += created
                users_updated += 1
                self.stdout.write(
                    f'  - {user.email}: {created} categorías creadas'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nResumen: {total_created} categorías creadas para {users_updated} usuarios'
            )
        )
