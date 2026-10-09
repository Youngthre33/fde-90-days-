#!/usr/bin/env bash
# Run as root through systemd-run. No database writes or image rebuilds.
set -euo pipefail

entry_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
app_dir=/home/ubuntu/ticket-app
fail() { printf '%s\n' "$*" >&2; exit 1; }
[[ "$EUID" -eq 0 ]] || fail 'Run with sudo systemd-run as documented.'
[[ -f "$entry_dir/Caddyfile" && -f "$entry_dir/compose.override.yaml" ]] || fail 'The two configuration files are missing.'
[[ -f "$app_dir/.env.compose" ]] || fail 'Existing server .env.compose is missing; do not create a new database configuration.'
cd -- "$app_dir"
docker compose --env-file .env.compose config --quiet
api_id="$(docker compose --env-file .env.compose ps -q api)"
db_id="$(docker compose --env-file .env.compose ps -q db)"
[[ -n "$api_id" && -n "$db_id" ]] || fail 'The existing api and db containers must be running.'
curl --noproxy '*' --fail --silent --show-error --max-time 10 http://127.0.0.1:8002/health
printf '\n'

# Do not replace an existing website, custom Caddyfile, or Compose override.
owned_caddy=false
if [[ -e /etc/caddy/Caddyfile ]]; then
    cmp -s "$entry_dir/Caddyfile" /etc/caddy/Caddyfile || fail 'An existing Caddyfile is present. Report this message for inspection; nothing was overwritten.'
    owned_caddy=true
fi
if [[ "$owned_caddy" == false ]] && [[ -n "$(ss -H -ltn '( sport = :80 or sport = :443 )')" ]]; then
    fail 'Port 80 or 443 is already occupied. Report ss -lntp before proceeding.'
fi
if [[ -e "$app_dir/compose.override.yaml" ]]; then
    cmp -s "$entry_dir/compose.override.yaml" "$app_dir/compose.override.yaml" || fail 'An existing Compose override is present. Nothing was overwritten.'
fi
for other_override in compose.override.yml Compose.override.yaml Compose.override.yml docker-compose.override.yml docker-compose.override.yaml; do
    [[ ! -e "$app_dir/$other_override" ]] || fail "An existing $other_override is present. Report this before proceeding."
done

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends debian-keyring debian-archive-keyring apt-transport-https curl ca-certificates gnupg
curl --fail --silent --show-error --location --retry 2 --connect-timeout 15 --max-time 120 https://dl.cloudsmith.io/public/caddy/stable/gpg.key -o "$entry_dir/caddy-stable.gpg.key"
gpg --batch --yes --dearmor --output /usr/share/keyrings/caddy-stable-archive-keyring.gpg "$entry_dir/caddy-stable.gpg.key"
curl --fail --silent --show-error --location --retry 2 --connect-timeout 15 --max-time 120 https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt -o /etc/apt/sources.list.d/caddy-stable.list
chmod 0644 /usr/share/keyrings/caddy-stable-archive-keyring.gpg /etc/apt/sources.list.d/caddy-stable.list
apt-get update
apt-get install -y caddy
caddy_version="$(caddy version | cut -d ' ' -f 1)"
dpkg --compare-versions "${caddy_version#v}" ge 2.11.0 || fail 'Caddy 2.11 or newer is required for public IP certificates.'
caddy validate --config "$entry_dir/Caddyfile" --adapter caddyfile
if [[ -e /etc/caddy/Caddyfile && "$owned_caddy" == false ]]; then
    cp -p -- /etc/caddy/Caddyfile "/etc/caddy/Caddyfile.before-ticket-$(date +%Y%m%d%H%M%S)"
fi
install -m 0644 "$entry_dir/Caddyfile" /etc/caddy/Caddyfile
if [[ ! -e "$app_dir/compose.override.yaml" ]]; then
    install -m 0644 "$entry_dir/compose.override.yaml" "$app_dir/compose.override.yaml"
fi
docker compose --env-file .env.compose config --quiet
docker update --restart unless-stopped "$api_id" "$db_id"

# Allow web ports only when UFW is already active; never change SSH rules.
if command -v ufw >/dev/null && LC_ALL=C ufw status | grep -q '^Status: active'; then
    ufw allow 80/tcp
    ufw allow 443/tcp
fi
systemctl enable docker caddy
systemctl restart caddy

# Keep certificate name verification enabled while connecting locally.
for attempt in {1..12}; do
    if curl --noproxy '*' --fail --silent --show-error --connect-timeout 3 --max-time 5 --connect-to 42.192.114.83:443:127.0.0.1:443 https://42.192.114.83/health; then
        printf '\nHTTPS_READY: https://42.192.114.83/web/\n'
        exit 0
    fi
    sleep 5
done
fail 'Caddy is running, but HTTPS has not passed verification yet. Inspect journalctl -u caddy --no-pager -n 80; do not bypass certificate checks.'
