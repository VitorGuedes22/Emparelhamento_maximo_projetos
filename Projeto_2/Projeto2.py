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

def geraGrafoComNota(entrada_alunos,entrada_projetos):
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
                #Cria aresta atribuindo a nota do aluno como peso
                Grafo.add_edge(aluno,projetoInteresse,weight=notaAluno)
    
    return Grafo

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

def emparelhamentoEstavelUmAluno(Grafo,projetos,alunos):
    stable_matching = {} #{projeto:aluno}

    #lista de alunos sem atributos
    students = list(alunos.keys())
    
    #faz eparelhamento enquanto tiver aluno sem ser avaliado
    while len(students) > 0:
        aluno = students.pop(0) #aluno atual
        alunoProjetosCandidato = Grafo[aluno]   #projetos que o aluno se candidata
        print(f"aluno: {aluno}")
        print(f"alunoProjetosCandidato: {alunoProjetosCandidato}")

        #verifica se pode ser aceito em algum projeto que e candidato
        for projeto in alunoProjetosCandidato:
            
            #Obtem nota minima para entrar no projeto
            peso_edge = alunoProjetosCandidato[projeto]["weight"]
            print(f"Peso do casamento proposto: {peso_edge}")

            #Se o projeto tiver aluno casado obtem nota do casamento
            if projeto in stable_matching.keys():
                #Obtem o aluno do casmento se ja existir
                student_marriage = stable_matching[projeto]

                #Obtem nota do casamento ja exitente para o projeto
                current_edge_data = Grafo.get_edge_data(projeto, student_marriage)
                current_weight = current_edge_data["weight"]

                print(f"Peso do casamento ja feito: {current_weight} {student_marriage} {projeto}")

            #Se nao exitir casamento para o projeto cria um
            if projeto not in stable_matching.keys():
                stable_matching[projeto] = {aluno:peso_edge}
                print(f"Casamento feito: {projeto} {aluno}")
                break 
            
            #verifica se a nota do aluno atual e maior do que a do casamento
            elif peso_edge > current_weight:
                current_student = stable_matching[projeto]

                #subtitui o aluno do casamento
                stable_matching[projeto] = aluno

                print(f"Casamento trocado {aluno}/{current_student}")
                #aluno volta aos alunos que devem ser avaliados
                students.append(current_student)

    return stable_matching

def emparelhamentoEstavel(Grafo,projetos,alunos):
    stable_matching = {} #{projeto:aluno}
    alunos = list(alunos)

    #faz eparelhamento enquanto tiver aluno sem ser avaliado
    while len(alunos) > 0:

        aluno = alunos.pop(0) #aluno atual
        alunoProjetosCandidato = Grafo.neighbors(aluno)  #projetos que o aluno se candidata
        notaAluno = Grafo.nodes[aluno]["nota"]  #Nota de argumento do aluno
        
        print(f"aluno: {aluno}")
        print(f"alunoProjetosCandidato: {alunoProjetosCandidato}")
        print(f"Nota do aluno {aluno}: {notaAluno}")

        for projeto in alunoProjetosCandidato:

            #Nota minima p/ entrar no projeto
            requesitoProjeto = Grafo.nodes[projeto]["nota"]

            if (notaAluno >= requesitoProjeto):
                quantVagasProjeto = Grafo.nodes[projeto]["vagas"]
                
                if quantVagasProjeto > 0:
                    if projeto not in stable_matching.keys():   
                        stable_matching[projeto] = {aluno:notaAluno}
                    else:
                        stable_matching[projeto][aluno] = notaAluno
                    
                    Grafo.nodes[projeto]["vagas"] = quantVagasProjeto - 1
                    break
                else:
                    notaMaisBaixaProjeto = min(stable_matching[projeto].values())

                    if notaAluno > notaMaisBaixaProjeto:
                        #Remove do projeto o aluno de nota mais baixa
                        alunosProjeto = stable_matching[projeto]
                        alunoMenorNotaProjeto = min(alunosProjeto, key=alunosProjeto.get)
                        stable_matching[projeto].pop(alunoMenorNotaProjeto)
                        
                        #O aluno que saiu do projeto volta aos alunos que devem ser avaliados
                        alunos.append(alunoMenorNotaProjeto)

                        #Aluno atual entra no projeto
                        stable_matching[projeto][aluno] = notaAluno

                        break
       
    return stable_matching


#Le arquivo de entrada e separa os dados dos projetos e alunos
entradaDados = open("entradaProj2TAG.txt","+r").readlines()
entrada_projetos = entradaDados[3:53]
entrada_alunos = entradaDados[56:]

#Trata dados dos projetos e alunos em dicionarios
entrada_projetos = project_data(entrada_projetos)
entrada_alunos = student_data(entrada_alunos)

#Gera grafo considerando aceitacao dos alunos nos projetos para as arestas
Grafo = geraGrafoComNota(entrada_alunos,entrada_projetos)

print(f"Total de vertices:{Grafo.number_of_nodes()} total de arestas:{Grafo.number_of_edges()}")
projetos,alunos = getBiparticao(Grafo)
print(f"Quantidade projeto:{len(list(projetos))}")
print(f"Quantidade alunos:{len(list(alunos))}")

stable_matching = emparelhamentoEstavel(Grafo,projetos,alunos)
print(stable_matching)

print(f"projetos:{list(stable_matching.keys())}")
print(f"quantidade de projetos:{len(stable_matching)}")


#max_matching = nx.max_weight_matching(Grafo, maxcardinality=True, weight="weigth")

#Obtem maior emparelhamento estavel para alunos e projetos
# emparelhamentosEstaveis = dict()
# for cont in range(10):
#     max_matching = nx.max_weight_matching(Grafo, maxcardinality=True, weight="weigth")
#     emparelhamentosEstaveis[cont] = {len(max_matching): max_matching}
#     print(f"Iteração {cont} com {len(max_matching)} arestas")

# tamanhosEmparelhamentos = emparelhamentosEstaveis.values()
# print(f"Tamanhos dos emparelhamentos:{tamanhosEmparelhamentos}")

# print(f"Emparelhamento máximo:{max(tamanhosEmparelhamentos)}")
#print(f"Quant arestas: {len(max_matching)}")

# if nx.bipartite.is_bipartite(Grafo):
#     projetos,alunos = getBiparticao(Grafo)
#     print(f"O Grafo avaliado é bipartido e possui {Grafo.number_of_nodes()} vertices com {Grafo.number_of_edges()} arestas\n")

#     for i in range(50): print("#", end =" ")
#     print(f"Particao de projetos:{projetos} \n")
#     for i in range(50): print("#", end =" ")
#     print(f"Particao de alunos:{alunos} \n")

#  else:
    #  print("O Grafo avaliado não possui bipartição")

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

