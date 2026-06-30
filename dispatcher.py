"""Ponto de entrada do pseudo-SO (o despachante). 

Uso:
    python3 dispatcher.py entradas/processes.txt entradas/files.txt entradas/string.txt

Le os tres arquivos de entrada, cria os processos, instancia os gerenciadores
e roda a simulacao. Ao final, imprime o mapa do disco e as faltas de pagina.
"""

import sys

from src.processo import Processo


def ler_processos(caminho_processes, caminho_string):
    """Le processes.txt e string.txt e retorna a lista de processos criados.

    Cada linha de processes.txt vira um Processo, com PID sequencial a partir de 0.
    A i-esima linha de string.txt e a string de paginas do i-esimo processo.
    """
    with open(caminho_string) as f:
        linhas_string = [linha.strip() for linha in f if linha.strip()]

    processos = []
    with open(caminho_processes) as f:
        for pid, linha in enumerate(l.strip() for l in f if l.strip()):
            campos = [int(x.strip()) for x in linha.split(",")]
            (ini, prio, cpu, mws, imp, scn, mdm, sata) = campos
            paginas = []
            if pid < len(linhas_string):
                paginas = [int(x.strip()) for x in linhas_string[pid].split(",")]
            processos.append(
                Processo(pid, ini, prio, cpu, mws, imp, scn, mdm, sata, paginas)
            )
    return processos


def ler_arquivos_disco(caminho_files):
    """Le files.txt e retorna (total_blocos, segmentos_ocupados, operacoes).

    segmentos_ocupados: lista de (nome, primeiro_bloco, qtd_blocos).
    operacoes: lista de (id_processo, codigo, nome, blocos) — blocos vale None no delete.
    """
    with open(caminho_files) as f:
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
        id_proc, codigo, nome = int(campos[0]), int(campos[1]), campos[2]
        blocos = int(campos[3]) if len(campos) > 3 else None
        operacoes.append((id_proc, codigo, nome, blocos))

    return total_blocos, segmentos, operacoes


def imprimir_identificacao(processo, frames_alocados):
    """Imprime o bloco 'dispatcher =>' de identificacao de um processo."""
    print("dispatcher =>")
    print(f"  PID: {processo.pid}")
    print(f"  frames: {frames_alocados}")
    print(f"  priority: {processo.prioridade}")
    print(f"  time: {processo.tempo_processador}")
    print(f"  printers: {processo.req_impressora}")
    print(f"  scanners: {processo.req_scanner}")
    print(f"  modems: {processo.req_modem}")
    print(f"  drives: {processo.req_sata}")
    print()


def main():
    """Orquestra a leitura das entradas e a execucao da simulacao."""
    if len(sys.argv) != 4:
        print("Uso: python3 dispatcher.py processes.txt files.txt string.txt")
        sys.exit(1)

    caminho_processes, caminho_files, caminho_string = sys.argv[1:4]

    processos = ler_processos(caminho_processes, caminho_string)
    total_blocos, segmentos, operacoes = ler_arquivos_disco(caminho_files)

    # TODO (integracao): instanciar Memoria, ES, Arquivos e Escalonador;
    # rodar o loop; imprimir operacoes de arquivo, mapa do disco e faltas por processo.
    print(f"Processos lidos: {len(processos)}")
    print(f"Disco: {total_blocos} blocos, {len(segmentos)} segmentos, "
          f"{len(operacoes)} operacoes")


if __name__ == "__main__":
    main()