"""Generate local Grafana credentials without overwriting an existing .env."""
import os
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / '.env'
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print('.env já existe; configuração preservada.')
        return
    with os.fdopen(fd, 'w') as stream:
        stream.write(f'GRAFANA_ADMIN_PASSWORD={secrets.token_urlsafe(24)}\n')
        stream.write('GRAFANA_PORT=3000\nPROMETHEUS_PORT=9090\n')
    print('.env criado. Usuário Grafana: admin. Consulte a senha no arquivo .env.')


if __name__ == '__main__':
    main()
