from django.core.management.base import BaseCommand
import requests
import sys


class Command(BaseCommand):
    help = 'Проверка здоровья приложения'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='http://localhost:8000/monitoring/health/',
            help='URL для проверки здоровья'
        )

    def handle(self, *args, **options):
        url = options['url']

        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if response.status_code == 200 and data.get('status') == 'healthy':
                self.stdout.write(
                    self.style.SUCCESS('✅ Приложение здорово')
                )
                self._print_details(data)
                return
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Приложение нездорово')
                )
                self._print_details(data)
                sys.exit(1)

        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка подключения: {str(e)}')
            )
            sys.exit(1)

    def _print_details(self, data):
        """Вывод деталей проверки"""
        checks = data.get('checks', {})

        for check_name, check_result in checks.items():
            status = '✅' if check_result.get('healthy') else '❌'
            details = check_result.get('details', '')
            self.stdout.write(f'  {status} {check_name}: {details}')
