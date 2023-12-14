import networkx as nx
import random
import subprocess
import sys
from contextlib import redirect_stdout
import os


def project_data(entrada_projetos):
    project_data = {}
    for linha in entrada_projetos:
        #Remove caracters especiais não uteis para analises
        linha = linha.replace("(","").replace(")","")
        projeto,vagas,nota = linha.split(",")

        #Popula o dicionario de projetos
        project_data[projeto] = (int(vagas.replace(" ","")),int(nota.replace(" ","")))  

    return project_data


def student_data(entrada_alunos):
    student_data = {}
    for linha in entrada_alunos:
        #Faz separação dos dados dos alunos
        aluno,atributos = linha.split(":")

        #Remove caracters especiais não uteis para analises
        atributos = atributos.replace("(", "").replace(")", "").replace(",", "").replace("\n", "")
        
        try:
            #Separa as preferencias e nota do aluno em variaveis diferentes
            preferencias = atributos.split(" ")
            nota = int(preferencias.pop(-1))
            
            #Popula o dicionario de alunos com os valores de seus atributos
            student_data[aluno] = (preferencias,nota)
        
        except:
            print(f"ERRO no aluno: {aluno} com {preferencias}")


    return student_data


def geraGrafo(entrada_alunos,entrada_projetos):
    Grafo = nx.Graph()

    #Passa os vertices dos projetos como particao 0
    for projeto,especificacoes in entrada_projetos.items():
        Grafo.add_node(projeto, vagas = especificacoes[0], 
                       nota = especificacoes[1], bipartite=0)

    #Passa dos vertices dos alunos particao 1
    for aluno,atributos in entrada_alunos.items():
        Grafo.add_node(aluno, vagas = 0, 
                       nota = atributos[1], bipartite=1)
        
        notaAluno = atributos[1]
        
        #Cria aresta somente com os projetos que aceitam a nota do aluno
        for projetoInteresse in atributos[0]:
            Grafo.add_edge(aluno,projetoInteresse,weight = notaAluno)
    
    return Grafo


def getBiparticao(Grafo):
    #Obtem particao zero 
    projetos = {vertice for vertice, atributos in Grafo.nodes(data=True) 
                if atributos["bipartite"] == 0}
    
    #Obtem a particao 1 subtraindo a particao zero do conjunto de vertices do grafo 
    alunos = set(Grafo) - projetos
    
    return projetos,alunos


def searchVertexDegree(G,attribute,value):
    desemparelhados = set()
    for node in G.nodes():
        # Verifica se o nó tem o atributo desejado
        if attribute in G.nodes[node] and G.nodes[node][attribute] == value and G.degree(node) == 0:
            desemparelhados.add(node)

    return desemparelhados


def galeShapley(Grafo,projetos,alunos):
    Grafo = Grafo.copy()
    alunos = list(alunos)   #garante que o objeto sera uma lita
    random.shuffle(alunos)  #Embaralha a lista
    stable_matching = {} #aluno projeto

    #faz eparelhamento enquanto tiver aluno sem ser avaliado
    while len(alunos) > 0:
        #numeroAleatorio = random.randint(0,len(alunos) - 1)
        aluno = alunos.pop(0) #aluno atual
        alunoProjetosCandidato = Grafo.neighbors(aluno)  #projetos que o aluno se candidata
        notaAluno = Grafo.nodes[aluno]["nota"]  #Nota de argumento do aluno
        
        for projeto in alunoProjetosCandidato:

            #Nota minima p/ entrar no projeto
            requesitoProjeto = Grafo.nodes[projeto]["nota"]
            quantVagasProjeto = Grafo.nodes[projeto]["vagas"]

            #Add o aluno ao projeto e decrementa vagas
            if quantVagasProjeto > 0:
                if (notaAluno >= requesitoProjeto):
                    if projeto not in stable_matching.keys():   
                        stable_matching[projeto] = {aluno:notaAluno}
                    else:
                        stable_matching[projeto][aluno] = notaAluno
                    
                    Grafo.nodes[projeto]["vagas"] = quantVagasProjeto - 1
                    break 
            
            elif projeto in stable_matching.keys():
                notaMaisBaixaProjeto = min(stable_matching[projeto].values())

                #Substitui o aluno de nota mais baixa no projeto
                if notaAluno > notaMaisBaixaProjeto:
                    #Remove do projeto o aluno de nota mais baixa
                    alunosProjeto = stable_matching[projeto]
                    alunoMenorNotaProjeto = min(alunosProjeto, key=alunosProjeto.get)
                    stable_matching[projeto].pop(alunoMenorNotaProjeto)
                    
                    #O aluno que saiu do projeto volta aos alunos que devem ser avaliados
                    alunos.append(alunoMenorNotaProjeto)

                    #Aluno atual entra no projeto
                    stable_matching[projeto][aluno] = notaAluno

                    print(f'Projeto:{projeto};{alunoMenorNotaProjeto} saiu, entrou {aluno} ')
                    break
    
    print('')

    return stable_matching

    

def GrafoEmparelhado(grafo,stable_matching,projetos,alunos):
    graph_matching = nx.Graph()
    derivacoes = ['A','B','C','D','E','F']
    
    projetosEmparelhados = set()
    alunosEmparelhados = set()

    for projeto,alunos_casados in stable_matching.items():
        projetosEmparelhados.add(projeto)
        
        for aluno in range(len(alunos_casados.keys())):
            #Cria um vertice de projeto e aluno para cada par (projeto,aluno)
            projeto_derivado = projeto + "_" + derivacoes[aluno]
            student = list(alunos_casados.keys())[aluno]
            
            alunosEmparelhados.add(student)

            #Divide projetos e alunos em particoes diferentes
            graph_matching.add_node(projeto_derivado,bipartite = 0)
            graph_matching.add_node(student,bipartite = 1)

            #Cria aresta (projeto,aluno)
            graph_matching.add_edge(projeto_derivado,student)

    print(f"Quantidade de alunos:{len(alunosEmparelhados)}")
    print(f"Quantidade de projetos:{len(projetosEmparelhados)}")

    #Obtem todos projetos e alunos que não formaram par
    projetosDesemparelhados = projetos - projetosEmparelhados
    alunosDesemparelhados = alunos - alunosEmparelhados

    graph_matching.add_nodes_from(projetosDesemparelhados,bipartite = 0)
    graph_matching.add_nodes_from(alunosDesemparelhados,bipartite = 1)

    return graph_matching


def imprimeEmparelhamento(emparelhamento):
    print(f"\n######################## Maior emparelhamento #######################")
    
    for projeto, aluno in emparelhamento.edges():
        print(f"{projeto} -- {aluno}")

    print(f"\nQuantidade de vagas preenchidas:{len(emparelhamento.edges())}")
        
    projetosDesemparelhados = searchVertexDegree(emparelhamento,"bipartite",0)
    alunosDesemparelhados = searchVertexDegree(emparelhamento,"bipartite",1)
    
    alunos = set(node for node, atributo in emparelhamento.nodes(data=True) if atributo.get('bipartite') == 1)
    alunos = alunos - alunosDesemparelhados
    print(f"Quantidade de alunos em projetos:{len(alunos)}")
    
    if len(projetosDesemparelhados) == 0:
        print(f"Todos projetos possuem alunos")
    else:
        print(f"Total de projetos sem alunos: {len(projetosDesemparelhados)}")

    
    if len(alunosDesemparelhados) == 0:
        print(f"Todos alunos estao em algum projeto")
    else:
        print(f"Total de alunos sem projeto: {len(alunosDesemparelhados)}")


def item(grafo):
    if nx.is_bipartite(grafo):
        print(f"O grafo é bipartido com {grafo.number_of_nodes()} vertices e {grafo.number_of_edges()} arestas")
        projetos,alunos = getBiparticao(grafo)
        print(f"Quantidade de vertices da particao de projetos:{len(list(projetos))}")
        print(f"Quantidade de vertices da particao de alunos:{len(list(alunos))}")

    else:
        print("O grafo nao possui biparticao")

    emparelhamentos = []

    for i in range(10):
        print(f"\n################### Iteracao {i} #####################")
        stable_matching = galeShapley(grafo,projetos,alunos)
        
        stable_matching_graph = GrafoEmparelhado(grafo,stable_matching,projetos,alunos)
        emparelhamentos.append(stable_matching_graph)

        edges = set(stable_matching_graph.edges())
        quantEdges = len(edges)
    
        if i == 0:
            print(f"Primeiro emparelhamento com {quantEdges} pares")

        else:
            arestas_anteriores = emparelhamentos[i - 1].edges()

            arestas_diferentes = edges.difference(arestas_anteriores)

            if len(arestas_diferentes) > 0:
                print(f"Houveram mudancas de {len(arestas_diferentes)} arestas:{arestas_diferentes}")
            else:
                print(f"Nao houveram mudancas de arestas;")

            
    maiorEmparelhamento = max(emparelhamentos, key=len)
    imprimeEmparelhamento(maiorEmparelhamento)
        


#Le arquivo de entrada e separa os dados dos projetos e alunos
entradaDados = open("entradaProj2TAG.txt","+r").readlines()
entrada_projetos = entradaDados[3:53]
entrada_alunos = entradaDados[56:]

#Trata dados dos projetos e alunos em dicionarios
entrada_projetos = project_data(entrada_projetos)
entrada_alunos = student_data(entrada_alunos)

#Define arquivo que obtera a saida do programa
nome_arquivo = 'saida.txt'

#Abre o arquivo de saida para escrita
with open(nome_arquivo, 'w') as arquivo_saida:
    #Redireciona a saída para o arquivo
    with redirect_stdout(arquivo_saida):
        Grafo = geraGrafo(entrada_alunos,entrada_projetos)
        item(Grafo)

os.startfile(nome_arquivo)
    
saidaTerminal = open(nome_arquivo,"+r").read()
print(saidaTerminal)
