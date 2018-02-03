source .env
gunicorn --workers=$((2 * $(getconf _NPROCESSORS_ONLN) + 1)) --log-file /var/log/gunicorn/gunicorn.log --log-level DEBUG  run:app &
