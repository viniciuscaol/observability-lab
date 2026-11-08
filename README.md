# Observability Lab

Monitoramento de um host Linux com **Prometheus, Node Exporter e Grafana**, executado em Docker Compose. O dashboard, a fonte de dados e as regras de alerta ficam versionados e são carregados automaticamente.

Projeto de portfólio voltado a infraestrutura e DevOps: coleta de métricas reais, consultas PromQL, diagnóstico de capacidade e teste de recuperação do monitoramento. Não exige conta em nuvem ou serviço pago.

## Iniciar

Requisitos: Linux com Docker Engine e Compose v2, Git e Python 3.10 ou superior. Referência de execução: Ubuntu 24.04. Os scripts Python usam apenas a biblioteca padrão.

```bash
git clone https://github.com/viniciuscaol/observability-lab.git
cd observability-lab
python3 scripts/init.py
docker compose up -d
```

Abra [Grafana](http://localhost:3000), entre com usuário `admin` e a senha gerada no arquivo `.env`. O dashboard **Linux Host | Observability Lab** já será a página inicial. Aguarde as primeiras coletas; os gráficos começam sem histórico.

O [Prometheus](http://localhost:9090) permite consultar métricas, conferir a saúde dos alvos e acompanhar os estados dos alertas.

| Serviço | Papel | Acesso |
| --- | --- | --- |
| Node Exporter | Coleta CPU, memória, filesystems e carga do Linux | Somente rede interna do Compose |
| Prometheus | Coleta a cada 15 s e avalia regras a cada 15 s | `http://localhost:9090` |
| Grafana | Dashboard com nove painéis e seletor de instância | `http://localhost:3000` |

As portas são publicadas apenas em `127.0.0.1`. Para executar em outro servidor, use um túnel SSH:

```bash
ssh -L 3000:127.0.0.1:3000 -L 9090:127.0.0.1:9090 usuario@servidor
```

Se as portas estiverem ocupadas, edite `GRAFANA_PORT` e `PROMETHEUS_PORT` no `.env` antes de iniciar. Atualize as URLs de acesso; o link de atalho dentro do dashboard usa a porta padrão do Prometheus.

## Dashboard e métricas

- Disponibilidade do coletor.
- Uso de CPU: média dos núcleos calculada a partir da taxa do contador de tempo ocioso.
- Memória: `100 × (1 − MemAvailable / MemTotal)`.
- Uso do filesystem raiz e histórico dos filesystems reais.
- Load average de um minuto e tabela de alertas em `firing`.

Load average não é percentual de CPU. A memória usa a estimativa disponível do Linux, que considera memória recuperável. Disco usa bytes disponíveis para usuários comuns e ignora filesystems temporários.

O Node Exporter recebe o filesystem do host em modo de leitura e compartilha seu namespace de processos, para medir o host Linux. Não usa modo privilegiado nem monta o socket do Docker. **Em Docker Desktop/WSL2, as métricas podem corresponder à VM Linux do Docker**, não ao sistema Windows/macOS. O projeto não lista processos individuais nem mede cada container.

## Alertas e demonstração

Inclui indisponibilidade do coletor por 30 s, CPU acima de 85% por 5 min, memória acima de 90% por 5 min e filesystem gravável acima de 85% por 10 min.

Para testar um alerta sem gerar carga no servidor:

```bash
python3 scripts/demo_alert.py
```

O script interrompe apenas o Node Exporter do laboratório, verifica o alerta disparado, reinicia o coletor e confirma a resolução. Resultado esperado: `DEMO_OK`. A operação leva aproximadamente um a dois minutos. Consulte [o runbook](docs/RUNBOOK.md) para investigar cada alerta.

Os alertas aparecem no Prometheus e no dashboard. **Não há Alertmanager nem envio de notificações externas** nesta versão.

## Validação

Verificar configuração e regras:

```bash
docker compose run --rm --no-deps --entrypoint /bin/promtool prometheus check config /etc/prometheus/prometheus.yml
docker compose run --rm --no-deps --entrypoint /bin/promtool prometheus test rules /etc/prometheus/tests/rules.test.yml
```

Teste completo, com o laboratório iniciado:

```bash
python3 scripts/smoke.py
```

Resultado esperado: `SMOKE_OK`. O teste confirma métricas reais, percentuais válidos, dados do filesystem raiz, dashboard provisionado, conexão da fonte Prometheus e ciclo de disparo/recuperação do alerta. Não execute duas demonstrações/testes simultaneamente, pois ambos interrompem o mesmo coletor.

O CI executa esses passos em Ubuntu com Docker. Os testes `promtool` usam séries sintéticas para conferir hosts saudáveis, limites e atrasos de CPU/memória/disco, exclusão de disco somente leitura e recuperação do coletor. Eles não exigem aumentar a carga do computador.

## Persistência e organização

Prometheus mantém até 7 dias de métricas, com limite de retenção de 1 GB para blocos históricos. WAL e outros arquivos podem fazer o volume ultrapassar esse tamanho. Grafana mantém seu banco em um volume separado. O `.env` é ignorado pelo Git e o gerador preserva arquivos existentes.

```text
compose.yaml                  Serviços, volumes e rede
prometheus/prometheus.yml     Coleta e avaliação
prometheus/rules.yml          Recording rules e alertas
prometheus/tests/             Casos de teste do promtool
grafana/provisioning/         Fonte e carregamento do dashboard
grafana/dashboards/            Dashboard em JSON
scripts/                      Inicialização, smoke test e demonstração
docs/RUNBOOK.md               Investigação e recuperação
```

Os painéis são mantidos pelo JSON versionado; edite o arquivo e aguarde a atualização automática do provisionamento. A interface não salva alterações nesses painéis.

Parar e preservar os dados:

```bash
docker compose down
```

Apagar **todas as métricas e os dados persistidos do laboratório**:

```bash
docker compose down --volumes
```

Versões das imagens fixadas no Compose: Prometheus 3.16.0, Node Exporter 1.12.1 e Grafana 13.3.0. É um laboratório local de nó único; alta disponibilidade, logs, tracing e notificação externa ficam como possíveis evoluções.

## Referências

- [Node Exporter: execução em Docker](https://github.com/prometheus/node_exporter#docker)
- [Prometheus: testes de regras](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/)
- [Grafana: provisionamento](https://grafana.com/docs/grafana/latest/administration/provisioning/)

Licença MIT, conforme `LICENSE`.
