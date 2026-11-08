"""Small HTTP helpers for the local lab (Python standard library only)."""
import base64
import json
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def settings():
    values = {}
    env_file = ROOT / '.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#'):
                key, value = line.split('=', 1)
                values[key.strip()] = value.strip()
    for key in ('GRAFANA_ADMIN_PASSWORD', 'GRAFANA_PORT', 'PROMETHEUS_PORT'):
        if key in os.environ:
            values[key] = os.environ[key]
    return values


def get(service, path, auth=False):
    config = settings()
    port = config.get(f'{service.upper()}_PORT', '3000' if service == 'grafana' else '9090')
    if not port.isdigit() or not 0 < int(port) < 65536:
        raise ValueError('Invalid local port')
    request = urllib.request.Request(f'http://127.0.0.1:{port}{path}')
    if auth:
        credentials = f'admin:{config["GRAFANA_ADMIN_PASSWORD"]}'
        token = base64.b64encode(credentials.encode()).decode()
        request.add_header('Authorization', f'Basic {token}')
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)


def query(expression):
    payload = get('prometheus', '/api/v1/query?' + urllib.parse.urlencode({'query': expression}))
    if payload.get('status') != 'success':
        raise RuntimeError('Prometheus query failed')
    return payload['data']['result']


def wait_for(description, check, timeout=150):
    deadline = time.monotonic() + timeout
    last = 'condition not met'
    while time.monotonic() < deadline:
        try:
            result = check()
            if result:
                print(f'OK: {description}', flush=True)
                return result
        except (OSError, ValueError, KeyError, RuntimeError) as error:
            last = type(error).__name__
        time.sleep(2)
    raise RuntimeError(f'Timeout: {description} ({last})')
