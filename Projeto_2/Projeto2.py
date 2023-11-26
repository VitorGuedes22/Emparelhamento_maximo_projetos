import networkx as nx
import pandas as pd
import networkx as nx
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from networkx.algorithms import community
from matplotlib import cm
import numpy as np
from community import community_louvain
from igraph import Graph

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
        
        except:
            print(f"ERRO no aluno: {aluno} com {preferencias}")

        #Popula o dicionario de alunos com os valores de seus atributos
        student_data[aluno] = (preferencias,nota)

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
        
        #Obtem nota do aluno para avaliar a criacao de aresta
        notaAluno = atributos[1]

        #Cria aresta somente com os projetos que aceitam a nota do aluno
        for projetoInteresse in atributos[0]:
            if notaAluno >= Grafo.nodes[projetoInteresse]["nota"]:
                Grafo.add_edge(aluno,projetoInteresse)
    
    return Grafo

def getBiparticao(Grafo):
    #Obtem particao zero 
    projetos = {vertice for vertice, atributos in Grafo.nodes(data=True) 
                if atributos["bipartite"] == 0}
    
    #Obtem a particao 1 subtraindo a particao zero do conjunto de vertices do grafo 
    alunos = set(Grafo) - projetos
    
    return projetos,alunos



entradaDados = open("entradaProj2TAG.txt","+r").readlines()
entrada_projetos = entradaDados[3:53]
entrada_alunos = entradaDados[56:]

entrada_projetos = project_data(entrada_projetos)
entrada_alunos = student_data(entrada_alunos)

Grafo = geraGrafo(entrada_alunos,entrada_projetos)

if nx.bipartite.is_bipartite(Grafo):
    projetos,alunos = getBiparticao(Grafo)
    print(f"O Grafo avaliado é bipartido e possui {Grafo.number_of_nodes()} vertices com {Grafo.number_of_edges()} arestas\n")
    
    for i in range(50): print("#", end =" ")
    print(f"Particao de projetos:{projetos} \n")

    for i in range(50): print("#", end =" ")

    print(f"Particao de alunos:{alunos} \n")

else:
    print("O Grafo avaliado não possui bipartição")

# if nx.bipartite.is_bipartite(Grafo):
#     conjunto1, conjunto2 = nx.bipartite.sets(Grafo)
#     print("Conjunto 1:", conjunto1)
#     print("Conjunto 2:", conjunto2)
# else:
#     print("O grafo não é bipartido.")

#Grafo = Graph.from_networkx(Grafo)
#print(nx.is_bipartite(Grafo))
#print(Grafo)
#Grafo.add_nodes_from(entrada_projetos.keys(), bipartite = 0)
#Grafo.add_nodes_from(entrada_alunos.keys(), bipartite = 1)

