"""
Module with utility functions for generating visualisations of code
property graphs.
"""

import os
import subprocess
import tempfile

import numpy as np
import pandas as pd

from IPython.display import Image


def prolog_rule_to_dot(prolog_rule):
    """
    TODO: given a prolog rule (as a string), parse it and return the
    graphviz source of the code property graph it represents.
    """
    pass


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

    tmp_file = open(tmp_filename, "w")
    tmp_file.write(dot_source)
    tmp_file.close()

    render_graph(tmp_filename, filetype=filetype)
    image = Image(filename=tmp_filename + "." + filetype, embed=True, format=filetype)

    return image
