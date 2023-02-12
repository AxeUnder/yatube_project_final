from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    now_year = datetime.now().year
    return {
        'year': now_year
    }
