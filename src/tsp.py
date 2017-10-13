"""
巡回セールスマン問題(traveling salesman problem: TSP) を ACO で解くためのモジュール
"""
# coding: utf-8
import itertools
import math
import random

from aco import Agent, Node, Edge, Graph, MoveStrategyFactory

ALPHA = 1
BETA = 5
RHO = 0.3
Q = 100


class City(Node):
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


def heuristic(edge: Edge):
    return 1.0 / edge.from_node.distance(edge.to_node)


def assessment(edge: Edge):
    return (edge.pheromone ** ALPHA) * (heuristic(edge) ** BETA)


def length(city_list):
    prev = None
    total_length = 0

    for city in city_list:
        total_length += prev.distance(city) if prev else 0
        prev = city

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
nodes = [City(random.randint(0, 100), random.randint(0, 100)) for i in range(6)]

for from_node, to_node in itertools.combinations(nodes, 2):
    graph.add_node(from_node)
    graph.add_node(to_node)

    e = Edge(from_node, to_node, pheromone=random.random())
    graph.add_edge(e)

min_len, max_len = calcminmax(nodes)
print('Min Length: {}'.format(min_len))
print('Max Length: {}'.format(max_len))


def iterate(p=False):
    agents = [Agent(graph, nodes[0], MoveStrategyFactory(assessment)) for i in range(20)]
    while True:
        if all([agent.move() is None for agent in agents]):
            break

    for edge in graph.edges:
        edge.set_pheromone(edge.pheromone * RHO)

    for agent in agents:
        l = length(agent.path.nodes)
        for edge in set(agent.path.edges):
            edge.set_pheromone(edge.pheromone + Q / l)

    if p:
        print(['{:.2f}'.format(length(agent.path.nodes) / min_len) for agent in agents])

for i in range(20):
    iterate(p=True)
