# Projeto de Emparelhamento Estável

## Sobre o Projeto
Este repositório contém o código e os resultados de um projeto que visa maximizar o número de estudantes beneficiados por projetos financiados e abertos à participação dos alunos em uma universidade determinada.

## Requisitos
- Python instalado na máquina. 
- Biblioteca NetworkX instalada. Você pode instalá-la usando o comando `pip install networkx`.

## Instruções para Usuários
1. Navegue até a pasta `dist`.
2. Certifique-se de que o Python esteja instalado na máquina.
3. Clique no arquivo executável para iniciar o programa.
4. Visualize os resultados da execução no arquivo `saida.txt` que será aberto automaticamente.

## Algoritmo Utilizado
O projeto utiliza o algoritmo Gale-Shapley para realizar um emparelhamento estável ao máximo nível possível.

## Código
O código realiza as seguintes etapas:

1. **Leitura e Processamento dos Dados**: Lê e processa os dados dos projetos e alunos a partir de um arquivo de entrada.
2. **Criação do Grafo**: Cria um grafo bipartido usando NetworkX, onde um conjunto de nós representa os alunos e o outro conjunto representa os projetos.
3. **Algoritmo Gale-Shapley**: Aplica o algoritmo Gale-Shapley para encontrar o emparelhamento estável.
4. **Geração de Resultados**: Cria um grafo dos emparelhamentos e imprime os resultados no terminal e em um arquivo de texto.

O código inclui funções para gerar o grafo (`geraGrafo`), realizar o emparelhamento (`galeShapley`), e imprimir os resultados (`imprimeEmparelhamento`). 

## Formato da Entrada
O arquivo de entrada deve estar no formato `entradaProj2TAG.txt` e deve seguir a estrutura abaixo:

### Dados dos Projetos
- Cada linha representa um projeto com o formato: `projeto, vagas, nota`
  - `projeto`: Nome do projeto.
  - `vagas`: Número de vagas disponíveis para o projeto.
  - `nota`: Nota mínima exigida para o projeto.

### Dados dos Alunos
- Cada linha representa um aluno com o formato: `aluno: preferencias nota`
- `aluno`: Nome do aluno.
- `preferencias`: Lista de projetos que o aluno deseja se candidatar, separados por espaço.
- `nota`: Nota do aluno.

## Explicação da Saída
O arquivo `saida.txt` gerado pelo programa contém as seguintes informações:

1. **Informações do Grafo**: Detalhes sobre a bipartição do grafo, incluindo o número de vértices e arestas.

2. **Emparelhamentos**: Para cada iteração do algoritmo Gale-Shapley, o arquivo lista o emparelhamento encontrado, mostrando quais projetos estão associados a quais alunos.

3. **Estatísticas de Emparelhamento**:
 - **Quantidade de vagas preenchidas**: Número total de pares (projeto, aluno) formados.
 - **Quantidade de alunos em projetos**: Número de alunos que foram alocados a projetos.
 - **Total de projetos sem alunos**: Projetos que não têm alunos alocados.
 - **Total de alunos sem projeto**: Alunos que não foram alocados a nenhum projeto.


## Referências
- Irving, R.W., & Manlove, D.F. (2007). The Stable Marriage Problem: Structure and Algorithms.
