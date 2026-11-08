"""Assert live metrics, provisioned dashboard, data source and alert lifecycle."""
import math
import subprocess
import sys

from client import ROOT, get, query, wait_for


def metric_ready(expression, percent=False):
    rows = query(expression)
    if not rows:
        return False
    for row in rows:
        value = float(row['value'][1])
        if not math.isfinite(value) or (percent and not 0 <= value <= 100.01):
            return False
    return True


def dashboard_ready():
    result = get('grafana', '/api/dashboards/uid/linux-host', auth=True)
    dashboard = result['dashboard']
    return result['meta']['provisioned'] and len(dashboard['panels']) == 9


def main():
    wait_for('Grafana saudável', lambda: get('grafana', '/api/health')['database'] == 'ok')
    wait_for('dashboard provisionado', dashboard_ready)
    wait_for('fonte Prometheus conectada', lambda: get(
        'grafana', '/api/datasources/uid/prometheus/health', auth=True)['status'] == 'OK')
    for expression in ('up{job="node"} == 1', 'node_memory_MemTotal_bytes{job="node"}',
                       'node_filesystem_size_bytes{job="node",mountpoint="/"}',
                       'lab:cpu_usage:percent', 'lab:memory_usage:percent',
                       'lab:filesystem_usage:percent{mountpoint="/"}'):
        wait_for(expression, lambda expression=expression: metric_ready(expression, 'percent' in expression))
    subprocess.run([sys.executable, 'scripts/demo_alert.py'], cwd=ROOT, check=True)
    print('SMOKE_OK: métricas reais, dashboard, datasource e ciclo do alerta verificados.')


if __name__ == '__main__':
    main()
