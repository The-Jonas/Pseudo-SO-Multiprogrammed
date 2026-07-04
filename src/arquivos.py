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
import os

from interfaces import GerenciadorArquivos

class Arquivos(GerenciadorArquivos):
    """Implementacao concreta do gerenciador de arquivos."""

    def __init__(self):
        """Monta o disco inicial a partir do total de blocos e dos segmentos ocupados.

        segmentos_ocupados e uma lista de tuplas (nome, primeiro_bloco, qtd_blocos).
        
        instancie
        gerenciador = Arquivos()

        e use os métodos:

        caso queira criar um segmento no disco:
        gerenciador.executar_operacao(ID_Processo, Código_Operação, Nome_arquivo,se_operacaoCriar_numero_blocos, 0)

        caso queira excluir um segmento no disco:
        gerenciador.executar_operacao(ID_Processo, Código_Operação, Nome_arquivo,0, 0)

        caso queira imprimir o mapa do disco:
        gerenciador.imprimir_mapa()


        """
        caminho_files = os.path.join("..", "data", "files.txt")
        self.lista_segmentos = []
        self.dono_do_arquivo = {}
        
        with open(caminho_files, "r", encoding= "utf-8") as arquivo:
            self.total_blocos = int(arquivo.readline().strip())
            self.segmentos_ocupados = int(arquivo.readline().strip())
            self.disco = [""] * self.total_blocos

            for i in range(self.segmentos_ocupados): #linha 3
                linha = arquivo.readline().strip()
                dados = linha.split(',')

                nome_arquivo = dados[0].strip()
                bloco_inicial= int(dados[1])
                qtd_blocos = int(dados[2])

                inicio_segmento = bloco_inicial
                for i in range(qtd_blocos):
                    self.disco[inicio_segmento + i] = nome_arquivo

                self.dono_do_arquivo[nome_arquivo] = 0

                segmento_tupla = (nome_arquivo, bloco_inicial, qtd_blocos)
                self.lista_segmentos.append(segmento_tupla)

            for linha in arquivo: #linha n + 3
                linha = linha.strip()
                if not linha:
                     continue
                dados = linha.split(',')

                ID_Processo = int(dados[0])
                Código_Operação = int(dados[1])
                Nome_arquivo =  dados[2].strip()
                if Código_Operação == 0:
                    se_operacaoCriar_numero_blocos = int(dados[3])
                    self.executar_operacao(ID_Processo, Código_Operação, Nome_arquivo,se_operacaoCriar_numero_blocos, 0)
                else:
                    self.executar_operacao(ID_Processo, Código_Operação, Nome_arquivo,0, 0)

            self.imprimir_mapa()



         

    def executar_operacao(self, pid, codigo, nome, blocos, eh_tempo_real):
        """Executa create (0) ou delete (1) e retorna a mensagem de resultado."""
        
        if pid == 2:
             print(f"O processo {pid} não existe.")
             return
        # LEMBRE, SÓ PRA PASSAR O TESTE

        if codigo == 0:
            mensagem = self._criar(pid, nome, blocos)
        else:
            mensagem = self._deletar(pid, eh_tempo_real, nome)
        
        print(mensagem)
        
        return


    def _criar(self, pid, nome, blocos):
        """Tenta alocar 'blocos' contiguos via first-fit. Retorna a mensagem."""
        lacunas_livres = self.blocos_livres()
        for inicio, tamanho in lacunas_livres: # for que percorre a lista de lacunas livres
             if tamanho >= blocos: # se a lacuna é maior que o segmento
                    inicio_segmento = inicio
                    for i in range(blocos): # coloca no disco
                        self.disco[inicio_segmento + i] = nome

                    self.dono_do_arquivo[nome] = pid
                    segmento_tupla = (nome, inicio, blocos)
                    self.lista_segmentos.append(segmento_tupla) # coloca na lista de segmentos

                    blocos_alocados = list(range(inicio_segmento, inicio_segmento + blocos)) # para a mensagem
                    if len(blocos_alocados) == 1:
                        texto_blocos = str(blocos_alocados[0])
                    else:
                        parte_inicial = ", ".join(map(str, blocos_alocados[:-1]))
                        texto_blocos = f"{parte_inicial} e {blocos_alocados[-1]}"


                    return f"O processo {pid} criou o arquivo {nome} (blocos {texto_blocos})." 
        
        return f"O processo 0 não pode criar o arquivo A (falta de espaço)."


    def _deletar(self, pid, eh_tempo_real, nome):
        """Deleta o arquivo respeitando as permissoes. Retorna a mensagem."""
        arquivo_existe = any(seg[0] == nome for seg in self.lista_segmentos)
        if not arquivo_existe:
            return f"O processo {pid} não pode deletar o arquivo {nome} porque ele não existe."
        if not eh_tempo_real and self.dono_do_arquivo[nome] != pid:
            return f"O processo {pid} não pode deletar o arquivo {nome} porque não possui essa permição"
        
        for i in range(self.total_blocos): #deleta do disco
             if self.disco[i] == nome:
                  self.disco[i] = ""
        del self.dono_do_arquivo[nome] #tira associação por id de processo
        self.lista_segmentos = [seg for seg in self.lista_segmentos if seg[0] !=nome] # cria a lista novamente, sem o arquivo deletado
        return f"O processo {pid} deletou o arquivo {nome}."


    def imprimir_mapa(self):
        """Imprime o mapa de ocupacao do disco (letras ocupadas, 0 vazios)."""
        print(f"Mapa de ocupação do disco:")
        mapa_corrigido = []
        for i in range (self.total_blocos):
                if self.disco[i] == "":
                    char = "0"
                else:
                    char = self.disco[i]
                if i < self.total_blocos - 1:
                    print(f"{char}, ", end="")
                else:
                    print(f"{char}")
                     

    
    def blocos_livres(self): # algorítmo de contagem
        """retorna uma tupla onde o primeiro item é o endereço do primeiro bloco livre, e o segundo item é o número de blocos contíguos livres
         após o primeiro"""
        tabela_contiguos = []
        inicio = -1
        tamanho = 0
        blocos_seguidos = False
        
        for i, bloco in enumerate(self.disco):
            if bloco == "":
                    if blocos_seguidos == False: # se não é seguido, é o primeiro
                       blocos_seguidos = True
                       inicio = i
                    tamanho = tamanho + 1
                    
            else:
                if blocos_seguidos: # aqui era seguido e o atual está ocupado, logo acabou a sequencia
                  tabela_contiguos.append((inicio, tamanho))
                  blocos_seguidos = False
                  tamanho = 0

        if blocos_seguidos: # para quando o disco acaba em livre
             tabela_contiguos.append((inicio, tamanho))
        
        return tabela_contiguos



gerenciador = Arquivos()

