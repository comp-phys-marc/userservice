#!/usr/bin/env bash
celery -A app worker --loglevel=info --pool=solo --without-heartbeat -n userservice@%h -Q user