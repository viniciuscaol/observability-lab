# Diagnóstico dos alertas

Os alertas são avaliados pelo Prometheus a cada 15 segundos. A condição precisa durar o período `for` para mudar de `pending` para `firing`. Não há envio de mensagens ou e-mail nesta versão.

| Alerta | Condição | Duração | Primeira investigação |
| --- | --- | --- | --- |
| `NodeExporterDown` | `up{job="node"} == 0` | 30 s | `docker compose ps -a` e `docker compose logs --tail=50 node-exporter` |
| `HostHighCPU` | CPU média acima de 85% | 5 min | `top`, `ps -eo pid,comm,%cpu --sort=-%cpu` e carga no Grafana |
| `HostHighMemory` | Memória acima de 90%, usando MemAvailable | 5 min | `free -h` e `ps -eo pid,comm,%mem --sort=-%mem` |
| `HostDiskAlmostFull` | Filesystem gravável acima de 85% | 10 min | `df -hT` e investigação dos diretórios que cresceram |

As regras de capacidade têm limites didáticos; ajuste-os ao comportamento do ambiente antes de qualquer uso operacional. O alerta de disco usa espaço disponível para usuários comuns. A soma de uso e espaço reservado pode diferir do percentual exibido por outras ferramentas.

## Simular indisponibilidade

```bash
python3 scripts/demo_alert.py
```

O script espera o coletor estar disponível, para somente o serviço `node-exporter`, aguarda `NodeExporterDown` disparar e inicia o serviço novamente em um bloco `finally`. Confirma a recuperação e a resolução do alerta. Durante esse teste haverá uma lacuna esperada nas métricas.

Se o terminal ou o computador encerrar antes da recuperação, inicie manualmente:

```bash
docker compose start node-exporter
```

## Painéis sem dados

1. Aguarde até um minuto após iniciar; o cálculo de CPU precisa de amostras de contador.
2. Abra Prometheus → Status → Target health. O alvo `node-exporter:9100` deve estar `UP`.
3. Consulte `up{job="node"}` e `node_memory_MemTotal_bytes{job="node"}` na tela de consulta.
4. Verifique `docker compose logs --tail=100 node-exporter prometheus grafana`.
5. Confirme que o Docker está rodando em Linux. Em Docker Desktop, os valores podem representar a VM Linux, não o Windows/macOS.

Se o alvo for removido da configuração, `up == 0` não detecta sua ausência. O laboratório mantém um alvo estático; detecção de desaparecimento de inventário fica fora deste escopo.

## Credenciais e persistência

A senha inicial do Grafana fica no `.env`. O volume do Grafana preserva usuários e alterações de senha. Alterar apenas `.env` depois da primeira inicialização não troca a senha de um usuário já existente. Se trocar a senha pela interface, atualize também o `.env` para os scripts de teste usarem a senha atual.

Volumes são preservados em `docker compose down`. O comando `docker compose down --volumes` apaga métricas e configurações persistidas do laboratório.
