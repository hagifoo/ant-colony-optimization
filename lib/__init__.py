# coding: utf-8
import itertools
import math
import random


class Node:
    """Agent が立ち寄るポイント"""
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def distance(self, node):
        return math.sqrt((self.x - node.x) ** 2 + (self.y - node.y) ** 2)


class Edge:
    def __init__(self, from_node: Node, to_node: Node, pheromone: float, bidirectional: bool=True):
        self._from = from_node
        self._to = to_node
        self._bidirectional = bidirectional
        self._pheromone = pheromone

    def has_from(self, node: Node):
        if self._from == node:
            return True
        elif self._bidirectional and self._to == node:
            return True
        else:
            return False

    def get_to(self, node: Node):
        if not self.has_from(node):
            return None
        else:
            return self._to if self._from == node else self._from

    @property
    def pheromone(self):
        return self._pheromone

    def set_pheromone(self, pheromone):
        self._pheromone = pheromone

    @property
    def from_node(self):
        return self._from

    @property
    def to_node(self):
        return self._to


class Graph:
    def __init__(self):
        self._nodes = set()
        self._edges = set()

    def add_node(self, node: Node):
        self._nodes.add(node)

    def add_edge(self, edge: Edge):
        self._edges.add(edge)

    def edges_by_node(self, node: Node):
        return {e for e in self._edges if e.has_from(node)}

    @property
    def edges(self):
        return self._edges

    @property
    def nodes(self):
        return self._nodes


class Path:
    def __init__(self, start_node: Node):
        self._nodes = [start_node]
        self._edges = []

    def move_to(self, to_node, edge):
        self._nodes.append(to_node)
        self._edges.append(edge)

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    @property
    def current_node(self):
        return self._nodes[-1]


class MoveStrategy:
    def __init__(self, graph: Graph, path: Path, alpha: float=1, beta: float=5):
        self._graph = graph
        self._path = path
        self._alpha = alpha
        self._beta = beta

    def choose(self):
        current_node = self._path.current_node
        edges = self._graph.edges_by_node(current_node)
        visited_nodes = set(self._path.nodes)
        candidate_edges = {e for e in edges if e.get_to(current_node) not in visited_nodes}

        total = 0
        for edge in candidate_edges:
            total += self._assessment(edge)

        for edge in candidate_edges:
            yield edge.get_to(current_node), edge, self._assessment(edge) / total

    def _assessment(self, edge):
        return (edge.pheromone ** self._alpha) * (self._heuristic(edge) ** self._beta)

    def _heuristic(self, edge):
        return 1.0 / edge.from_node.distance(edge.to_node)


class Agent:
    def __init__(self, graph, start_node, move_strategy):
        self._graph = graph
        self._path = Path(start_node)
        self._move_strategy = move_strategy

    def move(self):
        next_node = None
        next_edge = None
        for node, edge, probability in self._move_strategy(self._graph, self._path).choose():
            next_node = node
            next_edge = edge

            if random.random() < probability:
                break

        if next_node is None:
            return None
        else:
            self._path.move_to(next_node, next_edge)
            return next_node

    @property
    def path(self):
        return self._path


def length(node_list):
    prev = None
    total_length = 0

    for node in node_list:
        total_length += prev.distance(node) if prev else 0
        prev = node

    return total_length


def calcminmax(nodes):
    min_len = None
    max_len = 0
    for ns in itertools.permutations(nodes[1:]):
        l = length([nodes[0]] + list(ns))
        if min_len is None:
            min_len = l
        if l < min_len:
            min_len = l
        if l > max_len:
            max_len = l

    return min_len, max_len


graph = Graph()
nodes = [Node(random.randint(0, 100), random.randint(0, 100)) for i in range(6)]

for from_node, to_node in itertools.combinations(nodes, 2):
    graph.add_node(from_node)
    graph.add_node(to_node)

    e = Edge(from_node, to_node, pheromone=random.random())
    graph.add_edge(e)

print(calcminmax(nodes))


def iterate(p=False):
    agents = [Agent(graph, nodes[0], MoveStrategy) for i in range(20)]
    while True:
        if all([agent.move() is None for agent in agents]):
            break

    for edge in graph.edges:
        edge.set_pheromone(edge.pheromone * 0.3)

    for agent in agents:
        l = length(agent.path.nodes)
        for edge in set(agent.path.edges):
            edge.set_pheromone(edge.pheromone + 100 / l)

    if p:
        print([length(agent.path.nodes) for agent in agents])

for i in range(100):
    iterate(p=i % 10 == 0)
