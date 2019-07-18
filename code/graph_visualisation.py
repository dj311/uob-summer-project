"""
Module with utility functions for generating visualisations of code
property graphs.
"""

import os
import subprocess
import tempfile

import numpy as np
import pandas as pd

from collections import defaultdict
from IPython.display import Image


def prolog_rule_to_dot(prolog_rule):
    """
    TODO: given a prolog rule (as a string), parse it and return the
    graphviz source of the code property graph it represents.
    """

    # Make rule a single line without messing up the splits we use later.
    prolog_rule = prolog_rule.replace("), \n\t", "), ")
    prolog_rule = prolog_rule.replace("),\n\t", "), ")
    prolog_rule = prolog_rule.replace(",\n\t", ",")
    # Remove whitespace and . at end
    prolog_rule = prolog_rule.strip().strip(".")

    head, body = prolog_rule.split(" :- ")

    goals = body.split(', ')

    ast_edges = []
    cfg_edges = []
    ref_edges = []
    ancestor_edges = []
    runs_before_edges = []
    node_properties = defaultdict(list)  # {node_name: [node_properties]}

    for goal in goals:
        *functors, arguments = goal.strip(")").split("(")

        if functors == ['ast']:
            start, end = arguments.split(',')
            ast_edges.append((start, end))

        elif functors == ['ancestor']:
            start, end = arguments.split(',')
            ancestor_edges.append((start, end))

        elif functors == ['cfg']:
            start, end = arguments.split(',')
            cfg_edges.append((start, end))

        elif functors == ['runs_before']:
            start, end = arguments.split(',')
            runs_before_edges.append((start, end))

        elif functors == ['ref']:
            start, end = arguments.split(',')
            ref_edges.append((start,end))

        else:
            [node_name] = arguments.split(',')
            node_property = '◦'.join(functors)
            node_properties[node_name].append(node_property)

    def make_dot_edge(edge):
        start, end = edge
        return start + " -> " + end

    cfg_dot_edgelist = '\n'.join(map(make_dot_edge, cfg_edges))
    ast_dot_edgelist = '\n'.join(map(make_dot_edge, ast_edges))
    ancestor_dot_edgelist = '\n'.join(map(make_dot_edge, ancestor_edges))
    runs_before_dot_edgelist = '\n'.join(map(make_dot_edge, runs_before_edges))
    ref_dot_edgelist = '\n'.join(map(make_dot_edge, ref_edges))

    node_labels = ''
    for name, properties in node_properties.items():
        node_labels += name + ' [label="' + ", ".join(properties) + ' : ' + name +'"] \n'

    return """
        digraph g {
            {  # NODE LABELS
                node[shape=box]
                """ + node_labels + """
            }
            {  # AST
                edge[color=green3, constraint=true]
                """ + ast_dot_edgelist + """
            }
            {  # ANCESTOR
                edge[color=green3, constraint=true, style=dashed]
                """ + ancestor_dot_edgelist + """
            }
            {  # CFG
                edge[color=red3, constraint=false]
                """ + cfg_dot_edgelist + """
            }
            {  # RUNS BEFORE
                edge[color=red3, constraint=false, style=dashed]
                """ + runs_before_dot_edgelist + """
            }
            {  # REF
                edge[color=blue3, constraint=false]
                """ + ref_dot_edgelist + """
            }
        }
    """




def c_source_to_dot(joern_rule):
    """
    TODO: given a prolog rule (as a string), parse it and return the
    graphviz source of the code property graph it represents.
    """
    pass


def render_graph(filename, filetype='png'):
    """
    Render the dot/graphviz source at <filename> into an image of
    format <filetype>, outputting to the file <filename.filetype>.
    """
    dot_process = subprocess.run(["dot", "-O", "-T" + filetype, filename])


def jupyter_display_graph(dot_source, filetype='png'):
    """
    Given some dot/graphviz source code, render and display the graph
    in the Jupyter notebook.

    Example:
      import graph_visualisation
      graph_visualisation.jupyter_display_graph("digraph g {a -> b -> c -> d -> a}")
      <picture of graph displayed in notebook>
    """
    tmp_filename = "/tmp/jupyter_tmp_image"

    tmp_file = open(tmp_filename, "w", encoding="utf-8")
    tmp_file.write(dot_source)
    tmp_file.close()

    render_graph(tmp_filename, filetype=filetype)
    image = Image(filename=tmp_filename + "." + filetype, embed=True, format=filetype)

    return image
