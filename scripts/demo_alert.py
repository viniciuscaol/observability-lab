"""Stop only the local exporter, observe firing, restart and confirm resolution."""
import subprocess

from client import ROOT, query, wait_for


def compose(*args):
    subprocess.run(['docker', 'compose', *args], cwd=ROOT, check=True)


def main():
    wait_for('coletor disponível', lambda: query('up{job="node"} == 1'))
    try:
        compose('stop', 'node-exporter')
        wait_for('NodeExporterDown em firing', lambda: query(
            'ALERTS{alertname="NodeExporterDown",alertstate="firing"} == 1'), timeout=120)
    finally:
        compose('start', 'node-exporter')
    wait_for('coletor recuperado', lambda: query('up{job="node"} == 1'))
    wait_for('alerta resolvido', lambda: not query('ALERTS{alertname="NodeExporterDown"}'))
    print('DEMO_OK: alerta disparou e foi resolvido sem gerar carga artificial.')


if __name__ == '__main__':
    main()
