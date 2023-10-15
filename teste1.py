def ground_truth(grafo):
    comunidades = dict()

    for vertice,dictDept in grafo.nodes(data = True):
        if not dictDept["dept"] in comunidades:
            comunidades[dictDept["dept"]] = {vertice}
        else:
            comunidades[dictDept["dept"]].add(vertice)

    return comunidades

def visualizaParticao(grafo,partition,nome):
    pos = nx.spring_layout(grafo)
    # color the nodes according to their partition
    num_partitions = len(partition.values())
    
    cmap = cm.get_cmap('viridis', num_partitions + 1)

    cores = {node: cmap(partition[node] / num_partitions) for node in partition}
    
    #nx.draw_networkx_nodes(grafo, pos, partition.keys(), node_size=40,cmap=cmap, node_color=list(partition.values()))
    nx.draw_networkx_nodes(G, pos, node_color=list(cores.values()), node_size=200, cmap=cmap)
    
    nx.draw_networkx_edges(grafo, pos, alpha=0.5)
    plt.show()
    #plt.savefig(nome + ".png")

def questao7(grafo):
    #descobrindo a melhor partição com a maior modularidade
    #particaoLouvain = community_louvain.best_partition(grafo,random_state=123)
    particaoGroundTruth = ground_truth(grafo)

    #visualizaParticao(grafo,particaoLouvain,"ParticaoLouvain")
    visualizaParticao(grafo,particaoGroundTruth,"ParticaoGroundTruth")
    #print(len(groundTruth))

#teste no git