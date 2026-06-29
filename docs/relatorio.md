# Relatorio — Pseudo-SO (FSO)

Grupo 09 — Universidade de Brasilia

## 1. Ferramentas e linguagens utilizadas

Python 3.10+, apenas biblioteca padrao. Ambiente UNIX.
(Justificar a escolha: prazo, dominio da equipe, adequacao a simulacao.)

## 2. Descricao teorica e pratica da solucao

### 2.1 Processos, filas e escalonador
(Filas: global, tempo real FIFO sem preempcao, 3 filas de usuario com feedback e
aging, quantum de 1ms. Modelo de simulacao sequencial por ticks — justificar por
que dispensa sincronizacao real de concorrencia.)

### 2.2 Memoria e E/S
(20 frames: 8 tempo real, 12 usuario. LRU local, pre-carga de 1 pagina, contagem
de faltas. Recursos de E/S com alocacao exclusiva sem preempcao.)

### 2.3 Sistema de arquivos
(Alocacao contigua, first-fit a partir do bloco 0, regras de permissao de
create/delete, mapa de ocupacao.)

## 3. Dificuldades encontradas e solucoes

(Cada membro descreve as dificuldades do seu modulo e como resolveu.)

## 4. Papel de cada aluno

- Aluno 1 (Joao Victor): nucleo — processos, filas, escalonador, integracao.
- Aluno 2: memoria e E/S.
- Aluno 3: sistema de arquivos.

## 5. Uso de IA

(Indicar se houve uso de IA e qual ferramenta — obrigatorio pela especificacao.)

## 6. Bibliografia

- Stallings, W. Operating Systems Internals and Design Principles, Pearson, 2009.
- Martin, R. C. Clean Code, Prentice Hall, 2008.
