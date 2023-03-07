import networkx as nx

from ..graph import Graph

class GraphIO:
    pass

class NetworkXGraphIO(GraphIO):
    def write_graph(self, in_graph, out_fmt, out_fname):
        G = in_graph
        nx_G = nx.Graph()