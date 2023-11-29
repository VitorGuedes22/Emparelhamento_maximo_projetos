import networkx as nx

# Exemplo de grafo bipartido com atributos numéricos
G = nx.Graph()
G.add_nodes_from(['A', 'B', 'C', 'D'], bipartite=0)
G.add_nodes_from(['1', '2', '3', '4'], bipartite=1)

# Atributos numéricos para os vértices do lado 'A'
nx.set_node_attributes(G, {'A': 5, 'B': 7, 'C': 3, 'D': 6}, name='weight')

# Atributos numéricos para os vértices do lado 'B'
nx.set_node_attributes(G, {'1': 4, '2': 6, '3': 2, '4': 5}, name='weight')

# Separando os conjuntos de vértices bipartidos
top_nodes = {n for n, d in G.nodes(data=True) if d['bipartite'] == 0}
bottom_nodes = set(G) - top_nodes

# Criando um grafo completo bipartido ponderado baseado nos pesos
weighted_edges = [(u, v, -abs(G.nodes[u]['weight'] - G.nodes[v]['weight'])) for u in top_nodes for v in bottom_nodes]
weighted_graph = nx.Graph()
weighted_graph.add_weighted_edges_from(weighted_edges)

# Encontrando o emparelhamento perfeito máximo no grafo ponderado
max_weight_matching = nx.max_weight_matching(weighted_graph, maxcardinality=True)

print("Emparelhamento máximo:")
for vertex in max_weight_matching:
    print(f"{vertex} está emparelhado com {max_weight_matching[vertex]}")
