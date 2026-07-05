"""Ponto de entrada do pseudo-SO (o despachante).

Uso:
    python dispatcher.py                                      # usa entradas/ automaticamente
    python dispatcher.py processes.txt files.txt string.txt  # arquivos explicitos

Le os tres arquivos de entrada, cria os processos, instancia os gerenciadores,
roda a simulacao e imprime o mapa do disco e as faltas de pagina ao final.
"""

import sys
import os
import io
import contextlib

from src.processo import Processo
from src.filas import GerenciadorFilas
from src.escalonador import Escalonador
from src.memoria import Memoria
from src.es import ES
from src.arquivos import Arquivos


PASTA_PADRAO = os.path.join(os.path.dirname(__file__), "data")


def ler_processos(caminho_processes, caminho_string):
    """Le processes.txt e string.txt e retorna a lista de processos criados.

    Cada linha de processes.txt vira um Processo, com PID sequencial a partir de 0.
    A i-esima linha de string.txt e a string de paginas do i-esimo processo.
    """
    with open(caminho_string, encoding="utf-8") as f:
        linhas_string = [linha.strip() for linha in f if linha.strip()]

    processos = []
    with open(caminho_processes, encoding="utf-8") as f:
        for pid, linha in enumerate(l.strip() for l in f if l.strip()):
            campos = [int(x.strip()) for x in linha.split(",")]
            ini, prio, cpu, mws, imp, scn, mdm, sata = campos
            paginas = []
            if pid < len(linhas_string):
                paginas = [int(x.strip()) for x in linhas_string[pid].split(",")]
            processos.append(
                Processo(pid, ini, prio, cpu, mws, imp, scn, mdm, sata, paginas)
            )
    return processos


def ler_arquivos_disco(caminho_files):
    """Le files.txt e retorna (total_blocos, segmentos_iniciais, operacoes).

    segmentos_iniciais: lista de (nome, primeiro_bloco, qtd_blocos).
    operacoes: lista de (id_processo, codigo, nome, blocos) — blocos e None no delete.
    """
    with open(caminho_files, encoding="utf-8") as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    total_blocos = int(linhas[0])
    n_segmentos = int(linhas[1])

    segmentos = []
    for linha in linhas[2:2 + n_segmentos]:
        nome, primeiro, qtd = [c.strip() for c in linha.split(",")]
        segmentos.append((nome, int(primeiro), int(qtd)))

    operacoes = []
    for linha in linhas[2 + n_segmentos:]:
        campos = [c.strip() for c in linha.split(",")]
        id_proc = int(campos[0])
        codigo  = int(campos[1])
        nome    = campos[2]
        blocos  = int(campos[3]) if len(campos) > 3 else None
        operacoes.append((id_proc, codigo, nome, blocos))

    return total_blocos, segmentos, operacoes


def main():
    """Orquestra a leitura das entradas e a execucao da simulacao.

    Pode ser chamado de duas formas:
      python dispatcher.py                                          # usa entradas/ automaticamente
      python dispatcher.py processes.txt files.txt string.txt       # arquivos explicitos
    """
    if len(sys.argv) == 1:
        # Sem argumentos: pega os arquivos da pasta entradas/ por padrao.
        caminho_processes = os.path.join(PASTA_PADRAO, "processes.txt")
        caminho_files     = os.path.join(PASTA_PADRAO, "files.txt")
        caminho_string    = os.path.join(PASTA_PADRAO, "string.txt")
        print(f"Usando arquivos de: {PASTA_PADRAO}\n")
    elif len(sys.argv) == 4:
        caminho_processes, caminho_files, caminho_string = sys.argv[1:4]
    else:
        print("Uso: python dispatcher.py [processes.txt files.txt string.txt]")
        print("     (sem argumentos usa a pasta entradas/ automaticamente)")
        sys.exit(1)

    # --- Leitura das entradas ---
    processos = ler_processos(caminho_processes, caminho_string)
    total_blocos, segmentos, operacoes = ler_arquivos_disco(caminho_files)

    # --- Instanciacao dos gerenciadores ---
    memoria  = Memoria()
    es       = ES()
    filas    = GerenciadorFilas()
    arquivos = Arquivos(total_blocos, segmentos, len(processos))

    # --- Execucao do escalonador (processos + impressao do dispatcher) ---
    escalonador = Escalonador(filas, memoria, es)
    escalonador.rodar(processos)

    # --- Sistema de arquivos (executado apos todos os processos terminarem) ---
    print("Sistema de arquivos =>")
    print()
    for numero, (pid, codigo, nome, blocos) in enumerate(operacoes, start=1):
        eh_tr = processos[pid].eh_tempo_real if pid < len(processos) else False
        blocos_val = blocos if blocos is not None else 0

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            arquivos.executar_operacao(pid, codigo, nome, blocos_val, eh_tr)
        mensagem = buffer.getvalue().strip()

        status = "Sucesso" if ("criou" in mensagem or "deletou" in mensagem) else "Falha"
        print(f"Operação {numero} => {status}")
        print(mensagem)
        print()

    # --- Mapa do disco ---
    arquivos.imprimir_mapa()
    print()

    # --- Faltas de pagina por processo ---
    print("Número de Faltas de Páginas por processo:")
    for processo in processos:
        faltas = memoria.total_faltas(processo.pid)
        print(f"P{processo.pid} = {faltas} faltas de páginas")


if __name__ == "__main__":
    main()
