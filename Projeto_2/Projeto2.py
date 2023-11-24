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


entradaDados = open("entradaProj2TAG.txt","+r").readlines()
entrada_projetos = entradaDados[3:53]
entrada_alunos = entradaDados[56:]

entrada_projetos = project_data(entrada_projetos)
entrada_alunos = student_data(entrada_alunos)

Grafo = nx.DiGraph()

for projeto,especificacoes in entrada_projetos.items():
    Grafo.add_node(projeto, vagas = especificacoes[0], nota = especificacoes[1])

for aluno,atributos in entrada_alunos.items():
    Grafo.add_node(aluno, vagas = 0, nota = atributos[1])
    
    notaAluno = atributos[1]
    for projetoInteresse in atributos[0]:
        if notaAluno >= Grafo.nodes[projetoInteresse]["nota"]:
            Grafo.add_edge(aluno,projetoInteresse)

print(Grafo)

#Grafo.add_nodes_from(entrada_projetos.keys(), bipartite = 0)
#Grafo.add_nodes_from(entrada_alunos.keys(), bipartite = 1)

