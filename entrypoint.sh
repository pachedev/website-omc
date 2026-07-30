#!/bin/bash

set -e

# PostgreSQL connection, taken from environment variables
: ${HOST:=${DB_PORT_5432_TCP_ADDR:='postgres-runtime'}}
: ${PORT:=${DB_PORT_5432_TCP_PORT:=1920}}
: ${USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='odoo'}}}
: ${PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='odoo'}}}

# Build a runtime odoo.conf under /tmp with the credentials injected from the
# environment. The mounted config file is left untouched, so passwords are never
# written to disk.
ODOO_RC=/tmp/odoo-runtime.conf
cp /etc/odoo/odoo.conf "$ODOO_RC"
sed -i "s|^db_password\s*=.*|db_password = ${PASSWORD}|" "$ODOO_RC"
if [ -n "${ODOO_ADMIN_PASSWD}" ]; then
    sed -i "s|^admin_passwd\s*=.*|admin_passwd = ${ODOO_ADMIN_PASSWD}|" "$ODOO_RC"
fi
export ODOO_RC

# Install the project's extra Python dependencies, if any
if [ -f /etc/odoo/requirements.txt ]; then
    pip3 install -r /etc/odoo/requirements.txt
fi

# Odoo 12-14 images are based on Debian Buster (EOL). Its repositories are gone
# from deb.debian.org, so they are redirected to archive.debian.org before any
# apt-get call.
if grep -q "buster" /etc/apt/sources.list 2>/dev/null; then
    sed -i \
        -e 's|http://deb.debian.org/debian buster |http://archive.debian.org/debian buster |g' \
        -e 's|http://deb.debian.org/debian-security|http://archive.debian.org/debian-security|g' \
        -e 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' \
        /etc/apt/sources.list
    sed -i '/buster-updates/d' /etc/apt/sources.list
fi

# Install logrotate and cron if they are missing
if ! command -v logrotate &>/dev/null || ! command -v cron &>/dev/null; then
    apt-get update -qq && apt-get install -y -qq --no-install-recommends logrotate cron || true
fi

# Apply the logrotate configuration if one was provided
if [ -f /etc/odoo/logrotate ]; then
    cp /etc/odoo/logrotate /etc/logrotate.d/odoo
fi

# Start cron for logrotate. Non-fatal: some images do not ship it.
command -v cron &>/dev/null && cron || true

DB_ARGS=()
function check_config() {
    param="$1"
    value="$2"
    if grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then
        value=$(grep -E "^\s*\b${param}\b\s*=" "$ODOO_RC" |cut -d " " -f3|sed 's/["\n\r]//g')
    fi;
    DB_ARGS+=("--${param}")
    DB_ARGS+=("${value}")
}
check_config "db_host" "$HOST"
check_config "db_port" "$PORT"
check_config "db_user" "$USER"
check_config "db_password" "$PASSWORD"

case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec odoo "$@"
        else
            wait-for-psql.py ${DB_ARGS[@]} --timeout=30
            exec odoo "$@" "${DB_ARGS[@]}"
        fi
        ;;
    -*)
        wait-for-psql.py ${DB_ARGS[@]} --timeout=30
        exec odoo "$@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac

exit 1
