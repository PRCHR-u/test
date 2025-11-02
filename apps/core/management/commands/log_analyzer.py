from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Анализ логов приложения'

    def handle(self, *args, **options):
        log_file = settings.LOG_DIR / 'django.log'
        security_log_file = settings.LOG_DIR / 'security.log'
        business_log_file = settings.LOG_DIR / 'business.log'
        errors_log_file = settings.LOG_DIR / 'errors.log'

        self.stdout.write(self.style.SUCCESS('--- Анализ лог-файлов ---'))

        self._analyze_log(log_file, "Общий лог (django.log)")
        self._analyze_log(security_log_file, "Лог безопасности (security.log)")
        self._analyze_log(business_log_file, "Лог бизнес-логики (business.log)")
        self._analyze_log(errors_log_file, "Лог ошибок (errors.log)", level_filter='ERROR')

    def _analyze_log(self, log_file, title, level_filter=None):
        self.stdout.write(self.style.HTTP_INFO(f"\nАнализ: {title}"))
        if not log_file.exists():
            self.stdout.write(self.style.WARNING('Файл логов не найден'))
            return

        with open(log_file, 'r') as f:
            logs = f.readlines()

        total_lines = len(logs)
        error_count = sum(1 for log in logs if '[ERROR]' in log)
        warning_count = sum(1 for log in logs if '[WARNING]' in log)

        if level_filter:
            logs = [log for log in logs if f'[{level_filter}]' in log]

        self.stdout.write(f'Всего записей: {total_lines}')
        self.stdout.write(self.style.ERROR(f'Ошибки: {error_count}'))
        self.stdout.write(self.style.WARNING(f'Предупреждения: {warning_count}'))

        # Специфичная аналитика
        if 'security' in str(log_file):
            logins = sum(1 for log in logs if 'успешно вошел' in log)
            failed_logins = sum(1 for log in logs if 'Неудачная попытка входа' in log)
            self.stdout.write(self.style.SUCCESS(f'Успешных входов: {logins}'))
            self.stdout.write(self.style.NOTICE(f'Неудачных попыток входа: {failed_logins}'))

        if 'business' in str(log_file):
            creations = sum(1 for log in logs if 'создан' in log)
            updates = sum(1 for log in logs if 'обновлен' in log)
            debt_cleared = sum(1 for log in logs if 'очистил задолженность' in log)
            self.stdout.write(f'Создано объектов через API/Admin: {creations}')
            self.stdout.write(f'Обновлено объектов через API/Admin: {updates}')
            self.stdout.write(f'Операций по очистке долга: {debt_cleared}')
