# coding: utf-8
import random


class Node:
    """Agent が立ち寄るポイント"""
    pass


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
    def __init__(
            self, graph: Graph, path: Path, assessment_func):
        self._graph = graph
        self._path = path
        self._assessment = assessment_func

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


class MoveStrategyFactory:
    def __init__(self, assessment_func, strategy=MoveStrategy):
        self._assessment = assessment_func
        self._strategy = strategy

    def build(self, graph, path):
        return self._strategy(graph, path, self._assessment)


class Agent:
    def __init__(self, graph, start_node, move_strategy_factory):
        self._graph = graph
        self._path = Path(start_node)
        self._move_strategy_factory = move_strategy_factory

    def move(self):
        next_node = None
        next_edge = None
        for node, edge, probability in self._move_strategy_factory.build(self._graph, self._path).choose():
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
