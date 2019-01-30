#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 16:17:29 2018

@author: thasciano
"""

import requests
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms import bipartite
from operator import itemgetter
import pandas as pd
import seaborn as sns
from community import community_louvain # pip3 install python-louvain

anos = []

grau_medioDeputados = []
grau_maximoDeputados = []
grau_minimoDeputados = []
soma_pesosDeputados = []
numero_verticesDeputados = []
numero_arestasDeputados = []
distancia_mediaDeputados = []
densidadeDeputados = []
quantidade_comunidadesDeputados = []

grau_medioTemas = []
grau_maximoTemas = []
grau_minimoTemas = []
soma_pesosTemas = []
numero_verticesTemas = []
numero_arestasTemas = []
distancia_mediaTemas = []
densidadeTemas = []
quantidade_comunidadesTemas = []

idDeputadoNome = {}

anoTemasMaioresGraus = {}
anoEmparelhamentoMaximoTemas = {}
anoMaioresLigacoesTemas = {}

anoPartidoMaisPresente = {}
anoDeputadosMaiorProximidade = {}
anoDeputadosMaiorIntermediacao = {}

def idsSimProposicao(textoXml):
    root = ET.fromstring(textoXml)
    ids = []
    for votacao in root.find('Votacoes').findall('Votacao'):
        for voto in votacao.find('votos').findall('Deputado'):
            if voto.attrib['Voto'].strip() == 'Sim' :
                identificador = voto.attrib['ideCadastro']+"/"+voto.attrib['Partido'].strip()
                ids.append(identificador)
                if identificador not in idDeputadoNome.keys():
                    idDeputadoNome[identificador] = voto.attrib['Nome']
    return ids

def temasProposicao(textoXml):
    root = ET.fromstring(textoXml)
    temas = root.find('tema').text
    temas = temas.split('; ')
    return temas

def findCommunity(grafo):
    print("\nEncontra Partições:")
    partition = community_louvain.best_partition(grafo, weight='weight')
    #drawing
    size = float(len(set(partition.values())))
    pos = nx.spring_layout(grafo)
    count = 0.
    for com in set(partition.values()) :
        count = count + 1.
        list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
        nx.draw_networkx_nodes(grafo, pos, list_nodes, node_size = 20, node_color = str(count / size))
        nx.draw_networkx_edges(grafo, pos, alpha=0.5)
    print("Quantidade de Comunidades:" + str(count))
    plt.axis('off')
    print("=================GRAFO COMUNIDADES=======================")
    plt.show()
    return (count, partition)

def somaDosPesos(grafo):
    soma = 0
    for no, peso in grafo.degree(weight='weight'):
        soma = soma + peso
    return soma

def verticeMaiorPeso(grafo):
    maior = 0
    noMaiorPeso = ''
    for no, peso in grafo.degree(weight='weight'):
        if peso > maior:
            maior = peso
            noMaiorPeso = no
    return (noMaiorPeso, maior)

def analiseGrafo(grafo):
    print("Informações do grafo")
    print(nx.info(grafo))
    
    print("Centralidade de Grau")
    degc = nx.degree_centrality(grafo)
    print(sorted(degc.items(), key=itemgetter(1), reverse=True)[:10])
    
    print("Centraliade de Intermediação (Betweenness)")
    bet = nx.betweenness_centrality(grafo, weight='weight')
    print(sorted(bet.items(), key=itemgetter(1), reverse=True)[:10])
    
    print("Centralidade de Proximidade (Closeness)")
    clos = nx.closeness_centrality(grafo, distance='distance')
    print(sorted(clos.items(), key=itemgetter(1), reverse=True)[:10])
    
    print("Centralidade de Vetor Próprio")
    eig = nx.eigenvector_centrality(grafo, weight='weight')
    print(sorted(eig.items(), key=itemgetter(1), reverse=True)[:10])

    centrality_measures = {'Grau': degc, 'Betweenness': bet, 'Closeness': clos, 'Eigenvector': eig, }
    centrality = pd.DataFrame(centrality_measures)
    print(centrality[:10])
    sns.pairplot(centrality)
    
    print("=========ANÁLISE LEVANDO EM CONSIDERAÇÃO OS PESOS DAS ARESTAS===============")
    no_peso = verticeMaiorPeso(grafo)
    print('Nó com o maior grau (soma dos pesos): '+no_peso[0]+ ', com o peso: '+str(no_peso[1]))
    somaPesos = somaDosPesos(grafo)
    print('Soma de todos os pesos: '+str(somaPesos))
    

def grafoProjecaoTemas(temasDeputados, ano):
    grafoProjecao = nx.Graph(name='Projeção de temas - '+str(ano))
    grafoProjecao.add_nodes_from(temasDeputados.keys())
    chavesAnalisadas = []
    for chave, valores in temasDeputados.items():
        for chave2, valores2 in temasDeputados.items():
            if (chave != chave2) and (chave2 not in chavesAnalisadas):
                peso = 0
                for valor in valores:
                    if valor in valores2:
                        peso = peso + 1
                if peso > 0:
                    print(chave + " " + chave2)
                    grafoProjecao.add_edge(chave, chave2, weight=peso, distance = 1/peso)
        chavesAnalisadas.append(chave)
        
    grafoProjecao.remove_nodes_from(list(nx.isolates(grafoProjecao)))
    
    tuplaComunidade = findCommunity(grafoProjecao)
    quantidade = tuplaComunidade[0]
    quantidade_comunidadesTemas.append(quantidade)
    spring_pos = nx.spring_layout(grafoProjecao)
    nx.draw(grafoProjecao, node_size=35, with_labels=True, pos = spring_pos)
    analiseGrafo(grafoProjecao)
    print("=================GRAFO PROJEÇÃO TEMAS=======================")
    plt.show()
    
    numero_de_nos = grafoProjecao.number_of_nodes()
    print("Número de nós: "+str(numero_de_nos))
    numero_verticesTemas.append(numero_de_nos)
    
    numero_de_arestas = grafoProjecao.number_of_edges()
    print("Número de arestas: "+str(numero_de_arestas))
    numero_arestasTemas.append(numero_de_arestas)
    
    grau_maximo = verticeMaiorPeso(grafoProjecao)
    print("Grau máximo: "+str(grau_maximo[1]))
    grau_maximoTemas.append(grau_maximo[1])
    
    densidade = nx.density(grafoProjecao)
    print("Densidade: "+str(densidade))
    densidadeTemas.append(densidade)
    
#    clusterizacao = nx.average_clustering(grafoProjecao, weight='weight')
#    print("Clusterização média: "+str(clusterizacao))
#    clusterizacaoTemas.append(clusterizacao)
    
    somaPesos = somaDosPesos(grafoProjecao)
    print("Soma dos pesos: "+str(somaPesos))
    soma_pesosTemas.append(somaPesos)
    
    no_peso = verticeMaiorPeso(grafoProjecao)
    print("Vértice maior peso: "+str(no_peso))
    
    anoTemasMaioresGraus[ano] = no_peso[0]
    
    anoEmparelhamentoMaximoTemas[ano] = nx.max_weight_matching(grafoProjecao)
    print("Emparelhamento máximo do ano: "+str(anoEmparelhamentoMaximoTemas.get(ano)))
    
    listaMaioresConexoes = sorted(grafoProjecao.edges(data=True),key= lambda x: x[2]['weight'],reverse=True)
    anoMaioresLigacoesTemas[ano] = listaMaioresConexoes[:5]
    print("Lista maiores conexões ano:"+str(anoMaioresLigacoesTemas.get(ano)))
    
    
def grafoProjecaoDeputados(idsDeputados, temasDeputados, ano):
    grafoProjecao = nx.Graph(name='Projeção de deputados - '+str(ano))
    grafoProjecao.add_nodes_from(idsDeputados)
    idsAnalisados = []
    for idDeputado in idsDeputados:
        for idDeputado2 in idsDeputados:
            if (idDeputado != idDeputado2) and (idDeputado2 not in idsAnalisados):
                peso = 0
                for chave, valores in temasDeputados.items():
                    if (idDeputado in valores) and (idDeputado2 in valores):
                        peso = peso + 1
                if peso > 0:
                    grafoProjecao.add_edge(idDeputado, idDeputado2, weight=peso, distance = 1/peso)
        idsAnalisados.append(idDeputado)
        
    grafoProjecao.remove_nodes_from(list(nx.isolates(grafoProjecao)))
    
    tuplaComunidade = findCommunity(grafoProjecao)
    quantidade = tuplaComunidade[0]
    quantidade_comunidadesDeputados.append(quantidade)
    spring_pos = nx.spring_layout(grafoProjecao)
    nx.draw(grafoProjecao, node_size=35,pos = spring_pos)
    analiseGrafo(grafoProjecao)
    print("=================GRAFO PROJEÇÃO DEPUTADOS=======================")
    plt.show()
    
    numero_de_nos = grafoProjecao.number_of_nodes()
    print("Número de nós: "+str(numero_de_nos))
    numero_verticesDeputados.append(numero_de_nos)
    
    numero_de_arestas = grafoProjecao.number_of_edges()
    print("Número de arestas: "+str(numero_de_arestas))
    numero_arestasDeputados.append(numero_de_arestas)
    
    grau_maximo = verticeMaiorPeso(grafoProjecao)
    print("Grau máximo: "+str(grau_maximo[1]))
    grau_maximoDeputados.append(grau_maximo[1])
    
    densidade = nx.density(grafoProjecao)
    print("Densidade: "+str(densidade))
    densidadeDeputados.append(densidade)
    
#    clusterizacao = nx.average_clustering(grafoProjecao, weight='weight')
#    print("Clusterização média: "+str(clusterizacao))
#    clusterizacaoDeputados.append(clusterizacao)
    
    somaPesos = somaDosPesos(grafoProjecao)
    print("Soma dos pesos: "+str(somaPesos))
    soma_pesosDeputados.append(somaPesos)
    
    analiseMaiorComunidade(tuplaComunidade[1], grafoProjecao, ano)

def analiseMaiorComunidade(dicionarioComunidades, grafo, ano):
    #Descobrindo a maior comunidade
    listaComunidades = dicionarioComunidades.values()
    dicionarioAux = {}
    for x in listaComunidades:
        if x not in dicionarioAux.keys():
            dicionarioAux[x] = 1
        else:
            dicionarioAux[x] = dicionarioAux.get(x) + 1
    maior = 0
    numeroMaiorComunidade = 0
    for chave, valor in dicionarioAux.items():
        if valor > maior:
            maior = valor
            numeroMaiorComunidade = chave
            
    #Separando os nós da maior comunidade
    listaNosMaiorComunidade = []
    for chave, valor in dicionarioComunidades.items():
        if valor == numeroMaiorComunidade:
            listaNosMaiorComunidade.append(chave)
    #Descobrindo o partido com mais representante
    dicionarioAux = {}
    for chave, valor in dicionarioComunidades.items():
        if valor == numeroMaiorComunidade:
            partido = extraiPartido(chave)
            if partido not in dicionarioAux:
                dicionarioAux[partido] = 1
            else:
                dicionarioAux[partido] = dicionarioAux.get(partido) + 1
    maior = 0
    partido = ''
    for chave, valor in dicionarioAux.items():
        if valor > maior:
            maior = valor
            partido = chave
    #Criando subgrafo com nós da maior comunidade
    subGrafo = grafo.subgraph(listaNosMaiorComunidade)
    print("\n=====ANÁLISE DO MAIOR COMPONENTE DO GRAFO DE DEPUTADOS======\n")
    print("Partido com mais representantes no componente: "+partido)
    anoPartidoMaisPresente[ano] = partido
    
    clos = nx.closeness_centrality(subGrafo, distance='distance')
    print("\nDez deputados com maior centralidade de proximidade dentro do maior componente: ")
    listaProximidade = extraiNomesDeputadosLista(sorted(clos.items(), key=itemgetter(1), reverse=True)[:10])
    print(listaProximidade)
    anoDeputadosMaiorProximidade[ano] = listaProximidade
    
    bet = nx.betweenness_centrality(subGrafo, weight='weight')
    print("\nDez deputados com maior centralidade de intermediação dentro do maior componente: ")
    listaIntermediacao = extraiNomesDeputadosLista(sorted(bet.items(), key=itemgetter(1), reverse=True)[:10])
    print(listaIntermediacao)
    anoDeputadosMaiorIntermediacao[ano] = listaIntermediacao
    
def extraiNomesDeputadosLista(lista):
    listaDeputados = []
    for identificador, metrica in lista:
        nome = idDeputadoNome.get(identificador)
        listaDeputados.append(nome+"/"+extraiPartido(identificador))
    return listaDeputados
    
    
def extraiPartido(noDeputado):
    idDeputado, partido = noDeputado.split('/')
    return partido
            
    
def criaGrafico(nomeEixoY, nomeGrafico, lista):
    plt.plot(anos, lista, '-bo')
    plt.xlabel('Anos')
    plt.ylabel(nomeEixoY)
    plt.title(nomeGrafico)
    plt.show()
    
for ano in range(2010, 2019):
    idsDeputados = [] 
    temasDeputados = {} 
#    grafo = nx.Graph()
    arquivo = open("tipoNumeroAno.txt","r")
    print("\n=================COMEÇOU A EXECUÇÃO DO ANO: " + str(ano)+"=================")
    anos.append(ano)

    for linha in arquivo:
        linha = linha.split()
        if int(linha[3]) == ano:
            try:
                requestProposicao = requests.get("http://www.camara.leg.br/SitCamaraWS/Proposicoes.asmx/ObterProposicao?tipo="+linha[0]+"&numero="+linha[1]+"&ano="+linha[2]);
                requestVotacao = requests.get("http://www.camara.leg.br/SitCamaraWS/Proposicoes.asmx/ObterVotacaoProposicao?tipo="+linha[0]+"&numero="+linha[1]+"&ano="+linha[2]);
                temas = temasProposicao(requestProposicao.text)
                ids = idsSimProposicao(requestVotacao.text)

                for id in ids:
                    if id not in idsDeputados:
                        idsDeputados.append(id)
                for tema in temas:
                    if tema not in temasDeputados:
                        temasDeputados[tema] = ids
            except:
                pass
            
#    grafo.add_nodes_from(idsDeputados, bipartite=0)
#    grafo.add_nodes_from(temasDeputados.keys(), bipartite=1)
    
#    print("=================GRAFO DEPUTADOS-TEMAS=======================")
#    for idDeputado in idsDeputados:
#        for chave, valores in temasDeputados.items():
#            peso = 0
#            for valor in valores:
#                if valor == idDeputado:
#                    peso = peso + 1
#            if peso > 0:
#                grafo.add_edge(idDeputado, chave, weight=peso)
#    grafo.remove_nodes_from(list(nx.isolates(grafo)))
    #nx.draw(grafo)
    #plt.show()

    grafoProjecaoTemas(temasDeputados, ano)
    grafoProjecaoDeputados(idsDeputados, temasDeputados, ano)
    
print("=======GRÁFICOS SOBRE AS PROJEÇÕES DEPUTADOS==============")
criaGrafico('Número de Vértices', 'Número de vértices por ano', numero_verticesDeputados)
criaGrafico('Número de Arestas', 'Número de arestas por ano', numero_arestasDeputados)
criaGrafico('Grau Máximo', 'Grau máximo por ano', grau_maximoDeputados)
criaGrafico('Soma de todos os pesos', 'Soma dos pesos por ano', soma_pesosDeputados)
criaGrafico('Número de Comunidades', 'Número de comunidades por ano', quantidade_comunidadesDeputados)
criaGrafico('Densidade', 'Densidade por ano', densidadeDeputados)

print("=======GRÁFICOS SOBRE AS PROJEÇÕES TEMAS=============")
criaGrafico('Número de Vértices', 'Número de vértices por ano', numero_verticesTemas)
criaGrafico('Número de Arestas', 'Número de arestas por ano', numero_arestasTemas)
criaGrafico('Grau Máximo', 'Grau máximo por ano', grau_maximoTemas)
criaGrafico('Soma de todos os pesos', 'Soma dos pesos por ano', soma_pesosTemas)
criaGrafico('Número de Comunidades', 'Número de comunidades por ano', quantidade_comunidadesTemas)
criaGrafico('Densidade', 'Densidade por ano', densidadeTemas)

print("=======ANÁLISE TEMAS=============")
print('Anos com seus temas mais votados: ')
for ano, tema in anoTemasMaioresGraus.items():
    print (str(ano) + ": "+tema)
print('\nEmparelhamentos máximos por ano: ')
for ano, temas in anoEmparelhamentoMaximoTemas.items():
    print("\n"+str(ano)+": ")
    for tema1, tema2 in temas:
        print(tema1+", e "+tema2)
print('\nLigações mais fortes por ano: ')
for ano, lista in anoMaioresLigacoesTemas.items():
    print("\n"+str(ano)+": ")
    for tema1, tema2, atributos in lista:
        print(tema1+", e "+tema2)
        
print("\n=========ANÁLISE DEPUTADOS=========")
print('\nAnos com os partidos mais presentes no maior componente do grafo: ')
for ano, partido in anoPartidoMaisPresente.items():
    print (str(ano) + ": "+partido)
print('\nAnos com deputados com maior proximidade no maior componente do grafo: ')
for ano, lista in anoDeputadosMaiorProximidade.items():
    print("\n"+str(ano)+": ")
    for nome in lista:
        print(nome)
print('\nAnos com deputados com maior intermediação no maior componente do grafo: ')
for ano, lista in anoDeputadosMaiorIntermediacao.items():
    print("\n"+str(ano)+": ")
    for nome in lista:
        print(nome)        

print("\nTerminado com sucesso!")
