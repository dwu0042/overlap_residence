from dataclasses import dataclass
from collections import defaultdict
from typing import Any

import networkx as nx

__all__ = ['Interval', 'compute_shared_residence_times', 'make_overlap_graph', 'export_gml', 'export_graphviz']

@dataclass(order=True, frozen=True)
class Interval():
    """Interval contains information about an individual's (iden) tenure of stay (start, end) at location (loc)"""
    start: float
    end: float
    iden: Any=None
    loc: Any=None

    def __contains__(self, val):
        """If a value is within the time interval"""
        return self.start <= val <= self.end

    def overlaps(self, other):
        """If this interval overlaps (temporally and spatially) with another interval"""
        return (self.start <= other.end) and (other.start <= self.end) and self.loc == other.loc

    def amount_overlap(self, other):
        """The amount of time overlap between two intervals.
        Assumes and does not check that the two intervals overlap"""
        return min((other.end - self.start), (self.end - other.start))

def overlap_time(this, that):
    """Unitility function for computing the time overlap between two intervals"""
    if this.overlaps(that):
        return this.amount_overlap(that)
    else:
        return 0

def compute_shared_residence_times(data):
    """Construct a dictionary representation of overlaps in time and space
    
    """
    # assume data sorted by date
    # data structured as (id, loc, time start, time end)
    # want to output dict
    # id: 
    #   loc:
    #       other: duration
    residence = defaultdict(lambda: defaultdict(dict))
    active = set()
    for line in data:
        indv, loc, start, end = line
        interval = Interval(start, end, indv, loc)
        discard = []
        for other in active:
            if other.iden != indv and other.overlaps(interval):
                residence[indv][loc][other.iden] = other.amount_overlap(interval)
            if other.end < start:
                discard.append(other)
        for inactive in discard:
            active.discard(inactive)
        active.add(interval) 
    return residence

def make_overlap_graph(residence):
    """Make a tripartite graph of individuals-events-locations from the overlaps dict"""
    G = nx.MultiGraph()
    for selfnode, data in residence.items():
        G.add_node(selfnode, cls=0)
        for loc, overlap in data.items():
            G.add_node(loc, cls=2)
            for othernode, duration in overlap.items():
                G.add_node(othernode, cls=0)
                overlap_root = tuple(sorted((selfnode, othernode)) + [loc])
                i = 0
                while (*overlap_root, i) in G:
                    i += 1
                overlap_label = (*overlap_root, i)
                G.add_node(overlap_label, cls=1, duration=duration)
                G.add_edge(selfnode, overlap_label)
                G.add_edge(othernode, overlap_label)
                G.add_edge(overlap_label, loc)
    return G

def fold(G, cls):
    """Collapse the graph over a certain class of nodes"""
    pass

def export_gml(G, path):
    def stringizer(node):
        if isinstance(node, tuple):
            return '%'.join(str(x) for x in node)
        else:
            return str(node)
    nx.write_gml(G, path, stringizer=stringizer)

def export_graphviz(G, path):
    nx.nx_pydot.write_dot(G, path)