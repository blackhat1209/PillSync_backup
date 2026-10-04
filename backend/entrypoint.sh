#!/bin/sh
set -e
python manage.py migrate --noinput
if [ -n "$ADMIN_RESET_PASSWORD" ]; then
    python manage.py shell -c "from apps.accounts.models import User; u=User.objects.get(username='admin'); u.set_password('$ADMIN_RESET_PASSWORD'); u.save(); print('ADMIN PASSWORD RESET')"
fi
exec "$@"
