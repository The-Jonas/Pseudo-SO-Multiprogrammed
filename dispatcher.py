"""Ponto de entrada do pseudo-SO (o despachante).

Uso:
    python dispatcher.py                                      # usa entradas/ automaticamente
    python dispatcher.py processes.txt files.txt string.txt  # arquivos explicitos
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


PASTA_PADRAO = os.path.join(os.path.dirname(__file__), "entradas")


def ler_processos(caminho_processes, caminho_string):
    """Le processes.txt e string.txt e retorna a lista de processos criados."""
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
    """Le files.txt e retorna (total_blocos, segmentos_iniciais, operacoes)."""
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


def executar_operacoes_arquivo(operacoes, processos, pids_rejeitados, arquivos):
    """Executa as operacoes de arquivo respeitando o tempo_processador de cada processo.

    Cada operacao consome 1 unidade de tempo_processador do processo que a executa.
    Quando o processo esgota seu tempo (ou foi rejeitado), operacoes subsequentes
    daquele PID imprimem 'processo nao existe'.

    pids_rejeitados -- conjunto de PIDs que foram rejeitados pelo escalonador
    """
    # Creditos de operacoes por PID = tempo_processador original
    # PIDs rejeitados comecam com 0 creditos (nunca podem operar)
    creditos = {}
    for p in processos:
        if p.pid in pids_rejeitados:
            creditos[p.pid] = 0
        else:
            creditos[p.pid] = p.tempo_processador

    print("Sistema de arquivos =>")
    print()

    for numero, (pid, codigo, nome, blocos) in enumerate(operacoes, start=1):
        blocos_val = blocos if blocos is not None else 0

        # PID inexistente no processes.txt
        if pid >= len(processos):
            print(f"Operação {numero} => Falha")
            print(f"O processo {pid} não existe.")
            print()
            continue

        # Processo sem creditos: foi rejeitado ou ja esgotou o tempo
        if creditos.get(pid, 0) <= 0:
            print(f"Operação {numero} => Falha")
            print(f"O processo {pid} não existe.")
            print()
            continue

        # Consome 1 credito
        creditos[pid] -= 1

        eh_tr = processos[pid].eh_tempo_real

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            arquivos.executar_operacao(pid, codigo, nome, blocos_val, eh_tr)
        mensagem = buffer.getvalue().strip()

        status = "Sucesso" if ("criou" in mensagem or "deletou" in mensagem) else "Falha"
        print(f"Operação {numero} => {status}")
        print(mensagem)
        print()


def main():
    """Orquestra a leitura das entradas e a execucao da simulacao."""
    if len(sys.argv) == 1:
        caminho_processes = os.path.join(PASTA_PADRAO, "processes.txt")
        caminho_files     = os.path.join(PASTA_PADRAO, "files.txt")
        caminho_string    = os.path.join(PASTA_PADRAO, "string.txt")
        print(f"Usando arquivos de: {PASTA_PADRAO}\n")
    elif len(sys.argv) == 4:
        caminho_processes, caminho_files, caminho_string = sys.argv[1:4]
    else:
        print("Uso: python dispatcher.py [processes.txt files.txt string.txt]")
        sys.exit(1)

    processos = ler_processos(caminho_processes, caminho_string)
    total_blocos, segmentos, operacoes = ler_arquivos_disco(caminho_files)

    memoria  = Memoria()
    es       = ES()
    filas    = GerenciadorFilas()
    # Total de processos inclui todos — arquivos.py usa pids_rejeitados para filtrar
    arquivos = Arquivos(total_blocos, segmentos, len(processos))

    escalonador = Escalonador(filas, memoria, es)
    pids_rejeitados = escalonador.rodar(processos)

    executar_operacoes_arquivo(operacoes, processos, pids_rejeitados, arquivos)

    arquivos.imprimir_mapa()
    print()

    print("Número de Faltas de Páginas por processo:")
    for processo in processos:
        # Processos rejeitados nao aparecem nas faltas de pagina
        if processo.pid not in pids_rejeitados:
            faltas = memoria.total_faltas(processo.pid)
            print(f"P{processo.pid} = {faltas} faltas de páginas")


if __name__ == "__main__":
    main()
