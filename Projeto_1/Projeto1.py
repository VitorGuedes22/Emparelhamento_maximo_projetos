import networkx as nx
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from networkx.algorithms import community
from matplotlib import cm
import numpy as np
from community import community_louvain


#Função para retornar maior componente conectado contido no Grafo
def maiorComponente(grafo):
    # Cria lista de componentes do grafo
    componentes = nx.connected_components(grafo)

    #Cria dicionario de subGrafos contidos no grafo com tamanhos como chave
    subGrafos = {}
    for componente in componentes:
        subGrafo = grafo.subgraph(componente)
        subGrafos[subGrafo.size()] = subGrafo  #{numero de vertices: componente}

    #Obtem o maior subGrafo do conjunto
    maiorComponente = subGrafos[max(subGrafos.keys())]

    return maiorComponente



def gerarPng(grafo, nome):
    # Configura o layout do grafo
    pos = nx.spring_layout(grafo, seed=42)  # Experimente diferentes layouts conforme necessário
    
    # Desenha o grafo
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(grafo, pos, node_size=12, node_color='skyblue')
    nx.draw_networkx_edges(grafo, pos, edge_color='gray', alpha=0.5)

    #Adiciona rótulos aos vertices
    node_labels = {node: str(node) for node in grafo.nodes()}
    nx.draw_networkx_labels(grafo, pos, labels=node_labels, font_size=8)

    #Remove as limitações de dimensão na visualização
    plt.axis('off')
    
    #Cria um png e salva no diretorio do projeto
    plt.title(nome)
    plt.savefig(nome + ".png")

def visualizarParticao(grafo, partitions, nome):
    #Configura o layout 
    pos = nx.spring_layout(grafo,seed=42,k=0.2)
    
    #Obtem o numero de comunidades 
    num_partitions = len(partitions)

    #Obtem uma mapa de cores 
    cmap = cm.get_cmap('viridis', num_partitions + 1)

    comunidades = {}
    #Para cada vertice é atribuido uma comunidade 
    for community_id,nodes in enumerate(partitions):
        for node in nodes:
            comunidades[node] = community_id

    #Cria uma lista de codigos de cores
    cores =[]
    for community_id in comunidades.values():
        #Cada comunidade recebera um codigo de cor entre [0,1]
        cores.append(cmap(community_id / num_partitions))

    #Cria uma janela interna no layout para conter a imagem do grafo 
    fig, ax = plt.subplots()
    ax.scatter(*zip(*pos.values()), s=100, c=cores, edgecolors='k', cmap='viridis')

    #Desenja arestas
    nx.draw_networkx_edges(grafo, pos,ax=ax, alpha=0.5)

    #Adiona titulo 
    plt.title(nome)

    #Salva png do desenho no diretorio
    plt.savefig(nome + ".png")

def maiorClique(cliques):
    print(list(cliques))
    maiorClique = []
    for clique in list(cliques):
        if len(list(clique)) > len(maiorClique):
            maiorClique = clique
    
    return maiorClique

def ground_truth(grafo):
    comunidades = dict()

    for vertice,dictDept in grafo.nodes(data = True):
        if not dictDept["dept"] in comunidades:
            comunidades[dictDept["dept"]] = {vertice}
        else:
            comunidades[dictDept["dept"]].add(vertice)

    return comunidades


def questao4(grafo):
    maior = maiorComponente(grafo)

    print(f'Grafo com {grafo.number_of_nodes()} vertices, e {grafo.number_of_edges()} arestas')
    print(f'Maior componente conectado: {maior.number_of_nodes()} vertices, e {maior.number_of_edges()} arestas')

    gerarPng(maior,"MaiorComponenteConectado")


def questao5(grafo):
    #Cria uma partição de comunidades usando o algoritimo de Louvain e padroniza a geração usando a semente "123"
    particao = nx.community.louvain_communities(grafo,seed = 123)

    #Caulcula a mudularidade da partição em relação ao grafo
    modularidade = nx.community.modularity(grafo,particao)

    print(f'Partição com {len(particao)} comunidades')
    print(f'Maior comunidade com {len(max(particao, key=len))} vertices')
    
    print("Modularidade esperada em um grafo aleatorio NÃO ponderado e NÃO direcionado:[-0.5,1]")
    print(f"Modularidade encontrada na partição gerada pelo algoritmo de Louvain: {modularidade}")

    if modularidade > 0:
        print("Os vertices estão mais densamente conectados do que o esperado pelo acaso") 
    elif modularidade == 0: 
        print("Os vertices estão concetados com a densidade esperada pelo acaso")
    else:
        print("Os vertices estão menos densamente conectados do que o esperado pelo acaso")


def questao6(grafo):
    #Cria uma partição de comunidades usando o algoritimo de Louvain e padroniza a geração usando a semente "123"
    particao = list(nx.community.louvain_communities(grafo,seed = 123))

    #Obtem a modularidade da partição de ground truth
    groundTruth = list(ground_truth(grafo).values())
    
    #Caulcula as mudularidades das partições
    modularidadeLouvain = nx.community.modularity(grafo,particao)
    modularidadeGroundTruth = nx.community.modularity(grafo,groundTruth) 
    
    print(f'Modularidade do grafo usando Louvain: {modularidadeLouvain}')
    print(f'Modularidade obtida pela ground truth: {modularidadeGroundTruth}')

    if modularidadeLouvain > modularidadeGroundTruth:
        print("Partição de louvain apresenta maior densidade de conexões que a partição de ground truth")
    elif modularidadeLouvain < modularidadeGroundTruth:
        print("Partição de ground truth apresenta maior densidade de conexões que a partição de Louvain")





def questao7(grafo):
    #descobrindo a melhor partição com a maior modularidade
    particaoLouvain = list(nx.community.louvain_communities(grafo,seed = 123))

    #Obtendo a partição ground truth sendo comunidades de vertices do mesmo departamento
    particaoGroundTruth = list(ground_truth(grafo).values())

    #Gera um png para cada visualização das diferentes partições
    visualizarParticao(grafo,particaoLouvain,"Particao_Louvain")
    visualizarParticao(grafo,particaoGroundTruth,"Particao_Ground_Truth")


def deptComunidade(grafo,particao):
    #Atribui a cada departamento uma porcentagem zero
    departamentos = {}
    for vertice,atributos in grafo.nodes(data = True):
        if not atributos["dept"] in departamentos.keys():
            departamentos[atributos["dept"]] = 0
    
    #Cada comunidade recebe os departamentos com porcentagem inicial zero
    comunidades = {comunidade:departamentos for comunidade in range(len(particao))}

    #Passa a porcemtagem de cada departamento em cada comunidade
    for comunidade in comunidades:
        for dept in comunidades[comunidade]:
            frequencia = porcentagem(grafo,particao[comunidade],dept)
            comunidades[comunidade][dept] = frequencia

    return comunidades

def porcentagem(grafo,comunidade,dept):
    #Define um valor base para o numerador 
    numerador = 0

    #Busca frequencia do dept no na comunidade
    for vertice in comunidade:
        if grafo.nodes[vertice]["dept"] == dept:
            numerador += 1 

    #Retorna o valor da porcentagem
    return (numerador/len(comunidade)) * 100

def questao8(grafo):
    #Cria uma partição de comunidades usando o algoritimo de Louvain e padroniza a geração usando a semente "123"
    particao = nx.community.louvain_communities(grafo,seed = 123)

    #Obtem dict de porcentagens 
    #chave -> comunidade
    #valores -> dict de dept e porcentagem
    parametros = deptComunidade(grafo,particao)

    #Obtem lista de comunidades
    comunidades = parametros.keys()

    #Acessa os valores da primeira comunidade
    dept = parametros[list(parametros.keys())[0]]

    #Obtem as listas de departamentos
    departamentos = list(dept.keys())

    #Obtem as porcentagens de dept/comunidade
    porcentagens = []
    for comunidade in parametros.values():
        porcentagens.append(list(comunidade.values()))

    #Cria o data frame com os 3 paramentros necessarios para o mapa de calor
    dataFrame = pd.DataFrame(porcentagens,columns = departamentos, index = comunidades)
    
    #Colore o mapa com paleta de amarelo a azul
    plt.imshow(dataFrame, cmap ="YlGnBu")
    
    #Insere barra descritiva de cores em porcentagem
    barra_porcentagem = plt.colorbar()

    #Posiciona e descreve barra de porcentagem
    barra_porcentagem.set_label('Porcentagem', rotation=270, labelpad=15)
    
    #Rotula as linhas e colunas dentro dos intervalos existentes no mapa
    plt.xticks(range(len(dataFrame.columns)), dataFrame.columns, rotation='vertical')
    plt.yticks(range(len(dataFrame)), dataFrame.index)
    
    #Descreve dados dos eixos
    plt.xlabel("Departamento")
    plt.ylabel("Comunidade")

    #Adiciona titulo ao frame
    plt.title("Distribuição de departamentos por comunidade")
    
    #Visualiza o frame 
    plt.show()

    return

def questao9(grafo):
    #Cria uma lista com todos os cliques maximais do grafo
    cliques = nx.find_cliques(grafo)
 
    #Conta a quantidade de cliques maximais no grafo
    quantCliques = 0
    for clique in cliques:
        quantCliques += 1

    #Encontra o clique com maior numero de vertices na lista de cliques
    tamanhoMaioresCliques = len(max(nx.find_cliques(grafo), key=len))
    
    #Lista maiores cliques maximais do grafo
    maioresCliques = []
    for clique in nx.find_cliques(grafo):
        if len(clique) == tamanhoMaioresCliques:
            maioresCliques.append(clique)

    print(f'Quantidade de cliques no grafo: {quantCliques}')
    print(f'Ordem dos maiores clique maximais: {tamanhoMaioresCliques}')
    print(f'Quantidade de cliques maximais com a maior ordem:{len(maioresCliques)}')

    #Gera um subgrafo a partir de um dos maiores cliques maximais
    grafoClique = grafo.subgraph(maioresCliques[0])

    #Gera um png com o grafo do clique maximal marcado
    gerarPng(grafoClique,"MaiorClique")


def questao10(grafo):
    #Cria uma lista com todos os cliques do grafo
    cliques = nx.find_cliques(grafo)

    #Obtem ordem dos maiores cliques maximais
    tamanhoMaioresCliques = len(max(nx.find_cliques(grafo), key=len))

    #Gera lista com os maiores cliques maximais
    maioresCliques =[]
    for clique in cliques:
        if len(clique) == tamanhoMaioresCliques:
            maioresCliques.append(set(clique))

    #Gera grafo com todos vertices presentes nos maiores cliques maximais
    grafoCliques = nx.Graph()
    for clique in maioresCliques:
        if len(clique) == tamanhoMaioresCliques:
            grafoCliques.add_nodes_from(clique)
    
    #Adiciona as arestas ao grafo de vertices presentes nos maiores cliques maximais
    verticesGrafoClique = grafoCliques.nodes()
    for edge in grafo.edges():
        if (edge[0] in verticesGrafoClique) and (edge[1] in verticesGrafoClique):
            grafoCliques.add_edge(edge[0],edge[1])

    print(f'Ordem dos maiores cliques maximais:{tamanhoMaioresCliques}')
    print(f'Grafo reduzido aos vertices dos maiores cliques maximais:')
    print(grafoCliques)
    
    #Visualiza grafo por vertices 
    gerarPng(grafoCliques,"GrafoMaioresCliquesMaximais")

    #Visualiza grafo colorido por cliques
    visualizarParticao(grafoCliques,list(maioresCliques),"MaioresCliquesMaximais")

verticesRead = pd.read_csv("email_vertices.csv")
arestas = pd.read_csv("email_edgelist.csv")

#Cria dicionario de vertices como ID, e dept como atributo de cada vertice
vertices = {}
for _,vertice in verticesRead.iterrows():
    vertices[vertice["id"]] = {"dept": vertice["dept"]}

#Cria o grafo e passa os vertices
grafo = nx.Graph()
grafo.add_nodes_from(vertices.items())

#Passa as arestas ao grafo
for _,aresta in arestas.iterrows():
     grafo.add_edge(aresta["from"],aresta["to"])



#questao4(grafo)
#questao5(grafo)
#questao6(grafo)
#questao7(grafo)
#questao8(grafo)
#questao9(grafo)
#questao10(grafo)
#comentario teste git




    