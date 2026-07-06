"""Modulo de arquivos: sistema de arquivos em disco. 

Alocacao contigua com first-fit, sempre buscando a partir do bloco 0.
Regras de permissao:
  - Tempo real: cria (se houver espaco) e deleta qualquer arquivo.
  - Usuario: cria quantos quiser (se couber), mas so deleta os que criou.
O disco e uma lista: 0 indica bloco vazio, uma letra indica o arquivo ocupante.

Implementa a interface GerenciadorArquivos (ver src/interfaces.py).
Validacao: com o files.txt de exemplo, a saida deve bater com as paginas 6-7
da especificacao, e o mapa final fica: D D D Y 0 Z Z Z 0 0.
"""
import os

from src.interfaces import GerenciadorArquivos

class Arquivos(GerenciadorArquivos):
    """Implementacao concreta do gerenciador de arquivos."""

    def __init__(self, total_blocos, segmentos_iniciais, total_processos):
        """Monta o disco a partir dos dados ja lidos pelo dispatcher.

        Nao le arquivos: recebe os dados prontos para desacoplar da leitura.

        total_blocos      -- tamanho do disco em blocos
        segmentos_iniciais -- lista de (nome, primeiro_bloco, qtd_blocos)
        total_processos   -- quantidade de processos criados (para validar PIDs)
        """
        # __init__ nao le arquivo, nao executa operacoes e nao imprime mapa.
        # Tudo isso e responsabilidade do dispatcher, chamado apos o escalonador terminar.
        self.total_processos = total_processos
        self.disco = [""] * total_blocos
        self.total_blocos = total_blocos
        self.lista_segmentos = []
        self.dono_do_arquivo = {}
        self.espaco_livre = []

        for nome, bloco_inicial, qtd_blocos in segmentos_iniciais:
            nome = nome.strip()
            for i in range(qtd_blocos):
                self.disco[bloco_inicial + i] = nome
            self.dono_do_arquivo[nome] = None 
            self.lista_segmentos.append((nome, bloco_inicial, qtd_blocos))
        self._blocos_livres()




    def executar_operacao(self, pid, codigo, nome, blocos, eh_tempo_real):
        """Executa create (0) ou delete (1) e imprime a mensagem de resultado."""
        if pid >= self.total_processos:
            print(f"O processo {pid} não existe.")
            return

        if codigo == 0: 
            mensagem = self._criar(pid, nome, blocos)
        else:
            mensagem = self._deletar(pid, eh_tempo_real, nome)

        print(mensagem)


    def _criar(self, pid, nome, blocos):
        """Tenta alocar 'blocos' contiguos via first-fit. Retorna a mensagem."""
        for inicio, tamanho in self.espaco_livre :
            if tamanho >= blocos:
                for i in range(blocos):
                    self.disco[inicio + i] = nome
                self.dono_do_arquivo[nome] = pid
                self.lista_segmentos.append((nome, inicio, blocos))

                # Monta a descricao dos blocos alocados para a mensagem de sucesso.
                alocados = list(range(inicio, inicio + blocos))
                if len(alocados) == 1:
                    texto_blocos = str(alocados[0])
                else:
                    parte_inicial = ", ".join(map(str, alocados[:-1]))
                    texto_blocos = f"{parte_inicial} e {alocados[-1]}"
                self._blocos_livres()
                return f"O processo {pid} criou o arquivo {nome} (blocos {texto_blocos})."

        
        return f"O processo {pid} não pode criar o arquivo {nome} (falta de espaço)."


    def _deletar(self, pid, eh_tempo_real, nome):
        """Deleta o arquivo respeitando as permissoes. Retorna a mensagem."""
        arquivo_existe = any(seg[0] == nome for seg in self.lista_segmentos)
        if not arquivo_existe:
            return f"O processo {pid} não pode deletar o arquivo {nome} porque ele não existe."

        dono = self.dono_do_arquivo.get(nome)
        # Usuario so pode deletar arquivos que ele proprio criou.
        # Arquivos pre-existentes (dono None) so podem ser deletados por tempo real.
        if not eh_tempo_real and dono != pid:
            return (f"O processo {pid} não pode deletar o arquivo {nome} "
                    f"porque não possui essa permissão.")

        segmento = None
        inicio = 0
        tamanho = 0
        for seg in self.lista_segmentos:
            if seg[0] == nome: 
                segmento = seg
                inicio = segmento[1]
                tamanho = segmento[2]
                break

    

        for i in range(inicio, inicio + tamanho):
            if self.disco[i] == nome:
                self.disco[i] = ""
        del self.dono_do_arquivo[nome]
        self.lista_segmentos = [seg for seg in self.lista_segmentos if seg[0] != nome]
        self._blocos_livres()
        return f"O processo {pid} deletou o arquivo {nome}."


    def imprimir_mapa(self):
        """Imprime o mapa de ocupacao do disco (letras nos ocupados, 0 nos vazios).

        Formato: blocos separados por espaco, conforme o exemplo da especificacao.
        """
        print("Mapa de ocupação do disco:")
        mapa = []
        for bloco in self.disco:
            mapa.append(bloco if bloco != "" else "0")
        print(" ".join(mapa))

    def _blocos_livres(self):
        """Retorna lista de (inicio, tamanho) de regioes livres contiguas no disco."""
        tabela = []
        inicio = -1
        tamanho = 0
        em_sequencia = False

        for i, bloco in enumerate(self.disco):
            if bloco == "":
                if not em_sequencia:
                    em_sequencia = True
                    inicio = i
                tamanho += 1
            else:
                if em_sequencia:
                    tabela.append((inicio, tamanho))
                    em_sequencia = False
                    tamanho = 0

        if em_sequencia:
            tabela.append((inicio, tamanho))


        self.espaco_livre = tabela
        return 

