import networkx as nx
import random
import subprocess
import sys
from contextlib import redirect_stdout
import os
import copy


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


def galeyShapleyUmAluno(Grafo,projetos,alunos):
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


def galeyShapley1(Grafo,projetos,alunos1):
    alunos = list(copy.deepcopy(alunos1))
    Grafo = copy.deepcopy(Grafo)
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

            if (notaAluno >= requesitoProjeto):
                quantVagasProjeto = Grafo.nodes[projeto]["vagas"]
                
                #Add o aluno ao projeto e decrementa vagas
                if quantVagasProjeto > 0:
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

                        break
       
    return stable_matching

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

                #print(f"{aluno} {projeto}")

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

                    #print(f'{projeto}:{alunoMenorNotaProjeto} saiu, entrou {aluno} ')
                    break
    
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


def galeShapley2(projetos,alunos):
    alunos = alunos.copy()
    projetos = projetos.copy()
    a = list(alunos.keys())
    random.shuffle(a)
    stable_matching = {}

    while len(a) > 0:
        aluno = a.pop(0)
        argumento = alunos[aluno][1]

        for projeto in alunos[aluno][0]:
            if projetos.get(projeto) and projetos[projeto][0] > 0:
                vagas_projeto = projetos.get(projeto)[0]
                requisito_projeto = projetos.get(projeto)[1]

                if argumento >= requisito_projeto:
                    if projeto not in stable_matching:
                        stable_matching[projeto] = {aluno: argumento}
                    else:
                        stable_matching[projeto][aluno] = argumento

                    projetos[projeto] = (vagas_projeto - 1, requisito_projeto)
                    break
            else:
                if projeto in stable_matching:
                    alunos_projeto = stable_matching[projeto]
                    aluno_menor_nota_projeto = min(alunos_projeto, key=alunos_projeto.get)
                    menor_nota = alunos[aluno_menor_nota_projeto][1]

                    if argumento > menor_nota:
                        stable_matching[projeto].pop(aluno_menor_nota_projeto)
                        a.append(aluno_menor_nota_projeto)

                        stable_matching[projeto][aluno] = argumento
                        break

    return stable_matching


def item(grafo,p,a):
    if nx.is_bipartite(grafo):
        print(f"O grafo é bipartido com {grafo.number_of_nodes()} vertices e {grafo.number_of_edges()} arestas")
        projetos,alunos = getBiparticao(grafo)
        print(f"Quantidade de vertices da particao de projetos:{len(list(projetos))}")
        print(f"Quantidade de vertices da particao de alunos:{len(list(alunos))}")

    else:
        print("O grafo nao possui biparticao")

    emparelhamentos = []

    grafo2 = grafo.copy()
    for i in range(10):
        #grafo2 = grafo.copy()
        nodes1 = set(grafo2.edges())
        nodes2 = set(grafo.edges())
        if len(nodes2.difference(nodes1)) > 0:
            print("São diferentes")
        print(f"\n################### Iteracao {i} #####################")
        stable_matching = galeyShapley1(grafo,projetos,alunos)
        #stable_matching = galeShapley2(p,a)
        
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
        item(Grafo,entrada_projetos,entrada_alunos)

os.startfile(nome_arquivo)
    
saidaTerminal = open(nome_arquivo,"+r").read()
print(saidaTerminal)
