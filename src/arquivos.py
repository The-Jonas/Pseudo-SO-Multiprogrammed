"""Modulo de arquivos: sistema de arquivos em disco. 

Alocacao contigua com first-fit, sempre buscando a partir do bloco 0.
Regras de permissao:
  - Tempo real: cria (se houver espaco) e deleta qualquer arquivo.
  - Usuario: cria quantos quiser (se couber), mas so deleta os que criou.
O disco e uma lista: 0 indica bloco vazio, uma letra indica o arquivo ocupante.

Implementa a interface GerenciadorArquivos (ver src/interfaces.py).
Validacao: com o files.txt de exemplo, a saida deve bater com as paginas 6-7
da especificacao, e o mapa final fica: D D D Y _ Z Z Z _ _.
"""

from src.interfaces import GerenciadorArquivos


class Arquivos(GerenciadorArquivos):
    """Implementacao concreta do gerenciador de arquivos."""

    def __init__(self, total_blocos, segmentos_ocupados):
        """Monta o disco inicial a partir do total de blocos e dos segmentos ocupados.

        segmentos_ocupados e uma lista de tuplas (nome, primeiro_bloco, qtd_blocos).
        """
        # TODO: criar a lista do disco e marcar os blocos ja ocupados + donos
        raise NotImplementedError

    def executar_operacao(self, pid, codigo, nome, blocos):
        """Executa create (0) ou delete (1) e retorna a mensagem de resultado."""
        # TODO: validar processo, aplicar first-fit no create, checar dono no delete
        raise NotImplementedError

    def _criar(self, pid, nome, blocos):
        """Tenta alocar 'blocos' contiguos via first-fit. Retorna a mensagem."""
        # TODO
        raise NotImplementedError

    def _deletar(self, pid, eh_tempo_real, nome):
        """Deleta o arquivo respeitando as permissoes. Retorna a mensagem."""
        # TODO
        raise NotImplementedError

    def imprimir_mapa(self):
        """Imprime o mapa de ocupacao do disco (letras ocupadas, 0 vazios)."""
        # TODO
        raise NotImplementedError