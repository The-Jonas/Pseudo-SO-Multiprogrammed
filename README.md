# Pseudo-SO Multiprogrammed

**Sobre o Projeto**

Este projeto foi desenvolvido para a disciplina de **Fundamentos de Sistemas Operacionais (FSO) da Universidade de Brasília (UnB)** e tem como objetivo implementar um **pseudo-Sistema Operacional multiprogramado**, simulando os principais subsistemas de um SO real por meio de um modelo de execução sequencial determinístico.

O foco é o entendimento prático de escalonamento de processos, gerência de memória virtual, alocação de recursos de E/S e sistema de arquivos — avaliando criticamente as decisões de projeto e seus trade-offs em cada módulo.

🚀 **Funcionalidades Implementadas**

- *Escalonamento de processos de tempo real via FIFO sem preempção, com prioridade absoluta sobre processos de usuário.*
- *Escalonamento de processos de usuário com múltiplas filas de feedback, quantum de 1ms, preempção e aging para evitar starvation.*
- *Gerência de memória virtual por paginação com algoritmo LRU local por processo e contabilização de page faults.*
- *Alocação exclusiva e atômica de recursos de E/S (scanner, impressoras, modem, SATA), sem preempção e sem deadlock.*
- *Sistema de arquivos com alocação contígua via first-fit, operações de criação e deleção com controle de permissões por tipo de processo.*

---

## 📁 Estrutura do Projeto

```text
Pseudo-SO/
│
├── dispatcher.py              # Ponto de entrada — lê os arquivos, orquestra a simulação
│
├── src/                       # Módulos do pseudo-SO
│   ├── interfaces.py          # Contratos (assinaturas) dos gerenciadores
│   ├── processo.py            # Estrutura de dados do processo (PCB)
│   ├── filas.py               # Fila global, fila de tempo real e filas de usuário
│   ├── escalonador.py         # Loop de ticks, feedback, aging e integração dos módulos
│   ├── memoria.py             # Paginação com LRU local e contagem de page faults
│   ├── es.py                  # Alocação atômica de recursos de E/S
│   └── arquivos.py            # Sistema de arquivos: first-fit, create, delete e mapa do disco
│
├── entradas/
│   ├── processes.txt          # Processos a criar (exemplo da especificação)
│   ├── files.txt              # Estado inicial do disco e operações de arquivo
│   ├── string.txt             # Strings de referência de páginas por processo
│   └── testes/                # Conjuntos de entrada para cenários específicos
│
├── testes/
│   ├── teste_nucleo.py        # Teste isolado do escalonador com stubs
│   ├── teste_integracao.py    # Teste completo com gabarito da especificação
│   └── LEIA_OS_TESTES.md      # Explicação detalhada de cada cenário de teste
│
└── docs/
    ├── relatorio.md           # Rascunho do relatório técnico
    └── read_me.md             # Passo a passo de execução (versão PDF para entrega)
```

### 📌 Algoritmos e Conceitos Aplicados

**Escalonamento:** FIFO sem preempção (tempo real), Múltiplas Filas com Feedback (usuário), Aging para prevenção de starvation, Quantum de 1ms.

**Gerência de Memória:** Paginação com LRU local por processo, Pré-carga de 1 página, Separação de áreas (8 frames tempo real / 12 frames usuário).

**Gerência de E/S:** Alocação atômica (tudo-ou-nada), Exclusão mútua sem preempção, Rejeição de pedidos impossíveis na criação do processo.

**Sistema de Arquivos:** Alocação contígua, First-fit a partir do bloco 0, Controle de permissões (tempo real vs. usuário).

---

## ⚙️ Como rodar

#### *1. Requisitos*

Python 3.10+ — apenas biblioteca padrão, sem dependências externas.

#### *2. Execução com os arquivos de exemplo*

Clone o repositório e acesse a pasta do projeto:

```bash
git clone https://github.com/The-Jonas/Pseudo-SO-Multiprogrammed.git
cd Pseudo-SO-Multiprogrammed
```

Sem argumentos — usa automaticamente a pasta `entradas/`:

```bash
python dispatcher.py
```

Com arquivos explícitos (formato da especificação):

```bash
python dispatcher.py entradas/processes.txt entradas/files.txt entradas/string.txt
```

No Windows, use `python` em vez de `python3`. Em ambiente UNIX, ambos funcionam.

#### *3. Rodando com outros arquivos de teste*

```bash
python dispatcher.py entradas/testes/processes_usuario.txt entradas/testes/files_usuario.txt entradas/testes/string_usuario.txt
python dispatcher.py entradas/testes/processes_misto.txt   entradas/testes/files_misto.txt   entradas/testes/string_misto.txt
python dispatcher.py entradas/testes/processes_disco.txt   entradas/testes/files_disco.txt   entradas/testes/string_disco.txt
python dispatcher.py entradas/testes/processes_rejeicao.txt entradas/testes/files_rejeicao.txt entradas/testes/string_rejeicao.txt
```

Veja `testes/LEIA_OS_TESTES.md` para a explicação completa de cada cenário e a saída esperada.

#### *4. Rodando os testes automatizados*

```bash
python testes/teste_integracao.py   # valida saída completa contra o gabarito da spec
python testes/teste_nucleo.py       # valida o escalonador isoladamente com stubs
```

---

## 📋 Formato dos Arquivos de Entrada

#### `processes.txt` — um processo por linha

```
<tempo_inicializacao>, <prioridade>, <tempo_processador>, <max_working_set>, <impressora>, <scanner>, <modem>, <sata>
```

- `prioridade 0` = tempo real (FIFO, sem preempção, sem E/S)
- `prioridade 1, 2 ou 3` = usuário (quantum, feedback, aging)
- Recursos: `0` = não usa, `1` = usa

#### `files.txt` — estrutura em blocos

```
<total de blocos do disco>
<quantidade de arquivos já existentes>
<letra>, <bloco inicial>, <quantidade de blocos>    ← repete N vezes
<pid>, <código>, <nome>, <blocos se criar>          ← operações
```

- `código 0` = criar (inclui número de blocos)
- `código 1` = deletar (apenas o nome)

#### `string.txt` — uma linha por processo

```
<página>,<página>,<página>,...
```

Cada linha corresponde ao processo de mesmo índice em `processes.txt`. A string é percorrida integralmente durante a execução, independente do `tempo_processador`.

---

## 🛠️ Módulos e Decisões de Projeto

📌 **`processo.py`** — PCB do processo.
Mantém todos os atributos do processo: tempos, prioridade, working set, flags de recursos e ponteiro próprio na string de referência de páginas.

📌 **`filas.py`** — Estrutura de filas.
Fila de tempo real (deque FIFO) e três filas de usuário com feedback. Aging por limiar de espera (5 ticks) promove processos das filas baixas para evitar starvation.

📌 **`escalonador.py`** — Loop de simulação.
Relógio lógico de ticks. A cada tick: admite chegadas, executa tempo real inteiro ou usuário por 1 quantum, aplica aging. Aquisição atômica de E/S: processo só executa se conseguir todos os recursos de uma vez — sem recurso parcial retido, sem deadlock.

📌 **`memoria.py`** — Gerência de memória.
20 frames totais, separados em 8 (tempo real) e 12 (usuário) — áreas nunca compartilhadas. LRU aplicado localmente por processo. Pré-carga de 1 página por processo.

📌 **`es.py`** — Gerência de E/S.
1 scanner, 2 impressoras, 1 modem, 2 SATA. Alocação exclusiva sem preempção. Pedidos impossíveis (ex: 3 impressoras) rejeitam o processo na criação com mensagem de erro.

📌 **`arquivos.py`** — Sistema de arquivos.
Disco representado como lista de blocos. Alocação contígua via first-fit a partir do bloco 0. Tempo real pode criar e deletar qualquer arquivo; usuário só deleta os que criou.

---

## 📊 Cenários de Teste e Resultados

| Cenário | O que valida |
|---|---|
| Exemplo da especificação | Saída idêntica ao gabarito (exceto P0 faltas: 7 vs 6 por ambiguidade da pré-carga) |
| Usuários com recursos | Intercalamento por prioridade, contenção de E/S, permissões de arquivo |
| Misto TR + usuário | Prioridade absoluta do TR, TR deletando arquivo pré-existente |
| Disco cheio | Rejeição de criação, permissões de delete por tipo de processo |
| Rejeição de recursos | Processo rejeitado na criação por pedido impossível, sistema continua |

