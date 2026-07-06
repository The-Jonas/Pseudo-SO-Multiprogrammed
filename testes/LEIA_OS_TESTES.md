# Explicação dos testes

## Como rodar

```
python dispatcher.py entradas/testes/processes_X.txt entradas/testes/files_X.txt entradas/testes/string_X.txt
```

---

## Teste 1 — Usuários com recursos e contenção
**Arquivos:** `processes_usuario.txt`, `files_usuario.txt`, `string_usuario.txt`

### processes_usuario.txt
```
0, 1, 4, 3, 1, 0, 0, 0   → P0: chega no tick 0, prioridade 1 (usuário alta), 4 instruções, 3 frames, usa impressora
0, 2, 3, 3, 1, 0, 0, 0   → P1: chega no tick 0, prioridade 2 (usuário média), 3 instruções, 3 frames, usa impressora
0, 3, 2, 3, 0, 1, 0, 0   → P2: chega no tick 0, prioridade 3 (usuário baixa), 2 instruções, 3 frames, usa scanner
```

P0 e P1 disputam a impressora (só há 2). Como ambos pedem 1 e há 2 disponíveis, os dois conseguem.
P2 usa o scanner (único), então consegue também. O que o teste valida:
- Intercalamento correto por prioridade: P0 (prio 1) roda antes de P1 (prio 2) que roda antes de P2 (prio 3)
- Feedback: cada um roda 1 quantum e vai para fila menor

### files_usuario.txt
```
8                → disco com 8 blocos
2                → 2 arquivos já existentes
A, 0, 2          → arquivo A nos blocos 0 e 1
B, 4, 2          → arquivo B nos blocos 4 e 5
                 → estado inicial: A A _ _ B B _ _
0, 0, C, 2       → P0 cria C com 2 blocos → first-fit acha blocos 2 e 3 → SUCESSO
1, 1, A          → P1 tenta deletar A → P1 não criou A (dono é None=pré-existente) → FALHA permissão
2, 0, D, 3       → P2 cria D com 3 blocos → disco: A A C C B B _ _ → só 2 livres contíguos, não 3 → FALHA espaço
0, 1, B          → P0 tenta deletar B → P0 não criou B → FALHA permissão
1, 1, C          → P1 tenta deletar C → C foi criado por P0, não P1 → FALHA permissão
```

Mapa final esperado: `A A C C B B 0 0`

### string_usuario.txt
```
1,2,1,3   → P0 referencia páginas 1, 2, 1 (hit), 3 — com 3 frames: falta na 1, falta na 2, hit na 1, falta na 3 = 2 faltas (pré-carga desconta 1)
4,5,4     → P1 referencia 4, 5, 4 (hit) — 1 falta (pré-carga) + 1 falta na 5 = 1 falta útil... depende do LRU
6,1,2     → P2 referencia 6, 1, 2 — 3 frames, cada uma nova = faltas
```

---

## Teste 2 — Mistura de tempo real e usuário
**Arquivos:** `processes_misto.txt`, `files_misto.txt`, `string_misto.txt`

### processes_misto.txt
```
0, 0, 2, 4, 0, 0, 0, 0   → P0: tempo real, chega tick 0, 2 instruções, 4 frames, sem recursos
0, 1, 3, 3, 0, 1, 0, 0   → P1: usuário prio 1, chega tick 0, 3 instruções, 3 frames, usa scanner
2, 0, 2, 4, 0, 0, 0, 0   → P2: tempo real, chega tick 2, 2 instruções (entra depois de P0 terminar)
3, 2, 2, 3, 1, 0, 0, 0   → P3: usuário prio 2, chega tick 3, 2 instruções, usa impressora
```

O que o teste valida:
- Tempo real tem prioridade absoluta: P0 e P2 rodam inteiros antes de qualquer usuário
- P0 chega no tick 0 e roda imediatamente. P1 (usuário) fica esperando.
- P2 chega no tick 2 (tempo real) e interrompe a vez de P1.
- P1 e P3 só rodam depois que não há mais tempo real na fila.

### files_misto.txt
```
6                → disco com 6 blocos
1                → 1 arquivo existente
X, 0, 3          → arquivo X nos blocos 0, 1, 2
                 → estado inicial: X X X _ _ _
0, 0, Y, 2       → P0 (tempo real) cria Y → first-fit acha blocos 3 e 4 → SUCESSO
2, 1, X          → P2 (tempo real) deleta X → TR pode deletar qualquer arquivo → SUCESSO
1, 0, Z, 2       → P1 cria Z → blocos 0 e 1 livres (X foi deletado) → SUCESSO
3, 1, Y          → P3 tenta deletar Y → Y foi criado por P0, não P3 → FALHA permissão
```

Mapa final esperado: `Z Z 0 Y Y 0`

---

## Teste 3 — Disco cheio e permissões de tempo real
**Arquivos:** `processes_disco.txt`, `files_disco.txt`, `string_disco.txt`

### processes_disco.txt
```
0, 0, 2, 4, 0, 0, 0, 0   → P0: tempo real, 2 instruções
0, 1, 2, 3, 0, 0, 0, 0   → P1: usuário prio 1, 2 instruções
```

### files_disco.txt
```
6                → disco com 6 blocos
3                → 3 arquivos existentes
A, 0, 2          → A nos blocos 0 e 1
B, 2, 2          → B nos blocos 2 e 3
C, 4, 2          → C nos blocos 4 e 5
                 → estado inicial: A A B B C C  (disco 100% cheio)
0, 0, D, 1       → P0 tenta criar D com 1 bloco → disco cheio, zero livres → FALHA espaço
1, 1, A          → P1 (usuário) tenta deletar A → A é pré-existente (dono None), usuário não pode → FALHA permissão
1, 1, B          → P1 tenta deletar B → mesmo caso → FALHA permissão
0, 1, C          → P0 (tempo real) deleta C → TR pode deletar qualquer arquivo → SUCESSO
```

Mapa final esperado: `A A B B 0 0`

O que esse teste valida especificamente:
- Disco completamente cheio rejeita qualquer criação
- Usuário não pode deletar arquivos pré-existentes (dono = None)
- Tempo real pode deletar qualquer arquivo, mesmo pré-existente

---

## Teste 4 — Rejeição por pedido impossível de recursos
**Arquivos:** `processes_rejeicao.txt`, `files_rejeicao.txt`, `string_rejeicao.txt`

### processes_rejeicao.txt
```
0, 1, 2, 3, 3, 0, 0, 0   → P0: usuário prio 1, pede 3 impressoras (só existem 2) → REJEITADO na criação
0, 1, 2, 3, 1, 0, 0, 0   → P1: usuário prio 1, pede 1 impressora → admitido normalmente
0, 2, 2, 3, 0, 0, 2, 0   → P2: usuário prio 2, pede 2 modems (só existe 1) → REJEITADO na criação
```

O que o teste valida:
- Processo com pedido impossível é rejeitado na criação com mensagem de erro clara
- O sistema continua funcionando normalmente com os processos válidos
- Dois tipos de rejeição diferentes: impressora (limite 2, pediu 3) e modem (limite 1, pediu 2)

### files_rejeicao.txt
```
4                → disco com 4 blocos
0                → nenhum arquivo existente
                 → estado inicial: _ _ _ _
0, 0, A, 2       → P0 cria A com 2 blocos → first-fit acha blocos 0 e 1 → SUCESSO
1, 0, B, 2       → P1 cria B com 2 blocos → first-fit acha blocos 2 e 3 → SUCESSO
```

Nota: P0 foi rejeitado pelo escalonador mas o PID 0 ainda aparece nas operações de arquivo.
Isso é intencional — a spec não define como tratar operações de arquivo de processos rejeitados,
e o sistema de arquivos é independente do escalonador.

Mapa final esperado: `A A B B`

### string_rejeicao.txt
```
1,2,3   → P0 (rejeitado, nunca executa — 0 faltas)
4,5,6   → P1 referencia 3 páginas novas com 3 frames = 2 faltas (pré-carga desconta 1)
7,8,9   → P2 (rejeitado, nunca executa — 0 faltas)
```
