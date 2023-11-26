import networkx as nx
import matplotlib.pyplot as plt

# Criando um grafo simples
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5)])

# Encontrando o emparelhamento máximo
max_matching = nx.max_weight_matching(G)

print("Emparelhamento máximo:", max_matching)

# Desenhar o grafo
pos = nx.spring_layout(G)
plt.figure(figsize=(8, 6))
nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue')
nx.draw_networkx_edges(G, pos, edgelist=max_matching, edge_color='red', width=2)
plt.show()
