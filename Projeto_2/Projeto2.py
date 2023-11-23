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
        atributos = atributos.replace("(", "").replace(")", "").replace(",", "")
        
        #Separa as preferencias e nota do aluno em variaveis diferentes
        preferencias = atributos.split(" ")
        nota = preferencias.pop(len(preferencias) - 1)

        #Popula o dicionario de alunos com os valores de seus atributos
        student_data[aluno] = (preferencias,int(nota))

    return student_data

#for aluno,atributos in student_data(entrada_alunos).items():
#    print(f"Aluno:{aluno} Preferencias:{atributos[0]} Nota:{atributos[1]}")

entradaDados = open("entradaProj2TAG.txt","+r").readlines()
entrada_projetos = entradaDados[3:53]
entrada_alunos = entradaDados[56:]

entrada_projetos = project_data

Grafo = nx.Graph()
Grafo.add_nodes_from(project_data(entrada_projetos).items(), bipartite = 0)
Grafo.add_nodes_from(student_data(entrada_alunos).items(), bipartite = 1)

