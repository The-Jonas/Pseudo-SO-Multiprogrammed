# read_me — Pseudo-SO

## Requisitos
- Python 3.10 ou superior (apenas biblioteca padrao)

## Como executar
A partir da raiz do projeto:

```bash
python3 dispatcher.py entradas/processes.txt entradas/files.txt entradas/string.txt
```

## Arquivos de entrada
- `processes.txt`: um processo por linha. Campos:
  `tempo_inicializacao, prioridade, tempo_processador, max_working_set,
   req_impressora, req_scanner, req_modem, req_sata`
- `files.txt`: linha 1 = total de blocos; linha 2 = n segmentos ocupados;
  proximas n linhas = `arquivo, primeiro_bloco, qtd_blocos`;
  demais linhas = operacoes `id_processo, codigo, nome, qtd_blocos_se_criar`
  (codigo 0 = criar, 1 = deletar).
- `string.txt`: uma linha por processo, com a sequencia de paginas referenciadas.

## Observacoes
- O numero de linhas de `string.txt` deve ser igual ao de `processes.txt`.
- Os `id_processo` em `files.txt` so podem referenciar PIDs existentes (0 a N-1).
