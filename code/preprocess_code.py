"""
Module with utility functions for working with and preprocessing
source code.
"""

import clang.cindex
import gc
import json
import os
import snap
import subprocess
import swifter
import tempfile

import dask.dataframe as dd
import numpy as np
import pandas as pd

from tqdm import tqdm

import ast
from scipy import sparse
import networkx as nx

# This cell might not be needed for you.
clang.cindex.Config.set_library_file(
    '/lib/x86_64-linux-gnu/libclang-8.so.1'
)


def snap_graph_from_clang_ast(ast_root):
    """
    Given a concretised clang abstract syntax tree with node
    identifiers (i.e. you've run
        concretise_ast(ast_root)
        number_ast_nodes(ast_root)
    before calling this function), this outputs a directed graph
    compatible with the snap-python library:
        https://github.com/snap-stanford/snap-python
    """
    graph = snap.TNGraph.New()

    def walk_ast_and_construct_graph(node):
        graph.AddNode(node.identifier)

        for child in node.children:
            walk_ast_and_construct_graph(child)
            graph.AddEdge(node.identifier, child.identifier)

    walk_ast_and_construct_graph(ast_root)

    return graph


def concretise_ast(node):
    """
    Everytime you run .get_children() on a clang ast node, it
    gives you new objects. So if you want to modify those objects
    they will lose their changes everytime you walk the tree again.
    To avoid this problem, concretise_ast walks the tree once,
    saving the resulting list from .get_children() into a a concrete
    list inside the .children.
    You can then use .children to consistently walk over tree, and
    it will give you the same objects each time.
    """
    node.children = list(node.get_children())

    for child in node.children:
        counter = concretise_ast(child)


def number_ast_nodes(node, counter=1):
    """
    Given a concretised clang ast, assign each node with a unique
    numerical identifier. This will be accessible via the .identifier
    attribute of each node.
    """
    node.identifier = counter
    counter += 1

    node.children = list(node.get_children())
    for child in node.children:
        counter = number_ast_nodes(child, counter)

    return counter


def generate_edgelist(ast_root):
    """
    Given a concretised & numbered clang ast, return a list of edges
    in the form:
        [
            [<start_node_id>, <end_node_id>],
            ...
        ]
    """
    edges = []

    def walk_tree_and_add_edges(node):
        for child in node.children:
            edges.append([node.identifier, child.identifier])
            walk_tree_and_add_edges(child)

    walk_tree_and_add_edges(ast_root)

    return edges


def generate_features(ast_root):
    """
    Given a concretised & numbered clang ast, return a dictionary of
    features in the form:
        {
            <node_id>: [<degree>, <type>, <identifier>],
            ...
        }
    """
    features = {}

    def walk_tree_and_set_features(node):
        out_degree = len(node.children)
        in_degree = 1
        degree = out_degree + in_degree

        features[node.identifier] = [degree, str(node.kind), node.displayname]

        for child in node.children:
            walk_tree_and_set_features(child)

    walk_tree_and_set_features(ast_root)

    return features


def process_for_graph2vec(testcase, **kwargs):
    """
    Takes in a list of files/datapoints from juliet.csv.zip or
    vdisc_*.csv.gz (as loaded with pandas) matching one particular
    testcase, and preprocesses it ready for the baseline model.
    """
    parse_list = [
        (datapoint.filename, datapoint.code)
        for datapoint in testcase.itertuples()
    ]

    primary = find_primary_source_file(testcase)

    # Parse the source code with clang, and get out an ast:
    index = clang.cindex.Index.create()
    translation_unit = index.parse(
        path=primary.filename,
        unsaved_files=parse_list,
    )
    ast_root = translation_unit.cursor

    # Memoise/concretise the ast so that we can consistently
    # modify it, then number each node in the tree uniquely.
    concretise_ast(ast_root)
    number_ast_nodes(ast_root)

    # Next, construct an edge list for the graph2vec input:
    edgelist = generate_edgelist(ast_root)

    # Construct a list of features for each node
    features = generate_features(ast_root)

    graph2vec_representation = {
        "edges": edgelist,
        "features": features,
    }

    # Explicitly delete clang objects
    del translation_unit
    del ast_root
    del index

    return json.dumps(graph2vec_representation)


def process_for_node2vec(testcase, **kwargs):
    """
    By changing the function process_for_graph2vec, 
    just to get the edgelist, which can be used in 
    get node2vec and adjective matrix
    """
    parse_list = [
        (datapoint.filename, datapoint.code)
        for datapoint in testcase.itertuples()
    ]

    primary = find_primary_source_file(testcase)

    # Parse the source code with clang, and get out an ast:
    index = clang.cindex.Index.create()
    translation_unit = index.parse(
        path=primary.filename,
        unsaved_files=parse_list,
    )
    ast_root = translation_unit.cursor

    # Memoise/concretise the ast so that we can consistently
    # modify it, then number each node in the tree uniquely.
    concretise_ast(ast_root)
    number_ast_nodes(ast_root)

    # Next, construct an edge list for the graph2vec input:
    edgelist = generate_edgelist(ast_root)

    # Construct a list of features for each node

    # Explicitly delete clang objects
    del translation_unit
    del ast_root
    del index

    return edgelist


def find_primary_source_file(datapoints):
    """
    Given a list of datapoints representing the files for a single
    testcase, try to find which of the files is the "primary"
    file.

    According to the Juliet documentation, this should be the
    only file which defines the main function.

    In contrast, there is only ever one piece of code in the
    vdisc dataset.
    """

    if len(datapoints) == 1:
        # VDISC case and some of Juliet
        return datapoints.iloc[0]

    elif len(datapoints) > 1:
        # Juliet only case
        for datapoint in datapoints.itertuples():
            for line in datapoint.code.split("\n"):
                if line.startswith("int main("):
                    primary = datapoint

        return primary

    
def gen_adj_matrix(x):
    
    """
    Takes in a list of files/datapoints from buffer_overflow_data.csv.gz 
    matching one particular testcase, and generates an adjacency matrix 
    from the edgelist created.
    """
    G = nx.Graph()

    G.add_edges_from(x)

    A = nx.adjacency_matrix(G)

    B = A.todense()

    return B


def preprocess_all_for_node2vec(csv_location, num_partitions=20)
    """
    Given a data set (e.g. buffer_overflow_data.csv.gz) loaded in 
    as a pandas dataframe, it outputs all the edgelists files for
    ast tree.
    
    TODO: combine all_for_node2vec and all_for_adjmatrix into one
    """
    print("Preprocess our code so it can be used as an input into node2vec (egdelist).")
    data = pd.read_csv(csv_location)
    data = dd.from_pandas(data, npartitions=num_partitions)
    
    graphs = data.groupby(['testcase_ID']).apply(
        process_for_node2vec,
        axis='columns',
        meta=('processed_for_node2vec', 'unicode'),
    )
    
    print("`-> Finished prepping data for node2vec.")
    
    print("Making a directory to put our node2vec inputs into.")

    node2vec_input_dir = "../data/node2vec_input/"
    os.makedirs(node2vec_input_dir, exist_ok=True)

    print("Save to edgelists into txt files:")
    for index, row in graphs.iteritems():
        print("Current Iteration: "+str(index))
        with open(node2vec_input_dir + str(index) + ".txt", 'w') as f:  
            f.writelines("%s %s\n" % (parent,child) for parent, child in row)
            
    print("`-> Done.")

    return node2vec_input_dir



def preprocess_all_for_adjmatrix(csv_location, output_location="../data/adj.pickle", num_partitions=20):
    """
    Given a data set (e.g. buffer_overflow_data.csv.gz) loaded in 
    as a pandas dataframe, it gets the adj_matrix and then output
    into the pickle "adj.pickle".
    """
    print("Preprocess our code so it can be used as an input into node2vec (egdelist).")
    data = pd.read_csv(csv_location)
    data = dd.from_pandas(data, npartitions=num_partitions)
    
    graphs = data.groupby(['testcase_ID']).apply(
        process_for_node2vec,
        axis='columns',
        meta=('processed_for_node2vec', 'unicode'),
    )
    
    print("`-> Finished prepping data for node2vec.")
    
    print("Get a list for each datapoint:")
    
    from scipy import sparse
    
    df = []
    for index, row in graphs.iteritems():
        print("Current Iteration: "+str(index))
        df.append([index,sparse.csr_matrix(gen_adj_matrix(row))])
    
    print("Transfer list into dataframe format")
    
    adj = pd.DataFrame(df)
    
    import pickle
    # In case something wrong here
    print("Save the pickle")
    import pdb; pdb.set_trace()
    with open(output_location,'wb') as f:
        pickle.dump(adj,f)
    
    print("`-> Done.")

    return output_location
    

def preprocess_all_for_graph2vec(csv_location, output_location, num_partitions=20):
    """
    Given a data set (e.g. juliet.csv.zip or vdisc_*.czv.gz) loaded in
    as a pandas dataframe, it applies the graph2vec embedding to the
    abstract syntax tree of each piece of source code. This is then
    output into the file "../data/graph_embeddings.csv".
    """
    print("Preprocess our code so it can be used as an input into graph2vec.")

    data = pd.read_csv(csv_location)
    data = dd.from_pandas(data, npartitions=num_partitions)

    graphs = data.groupby(['testcase_ID']).apply(
        process_for_graph2vec,
        axis='columns',
        meta=('processed_for_graph2vec', 'unicode'),
    )

    print("`-> Finished prepping data for graph2vec.")

    # print("Dataset pre-processed for graph2vec. Saving to file:")
    # graphs.to_csv(tmp_directory.name + "/juliet_ready_for_graph2vec.csv.gz")
    # print("`-> Saved.")

    print("Making a temporary directory to put our graph2vec inputs into.")


    graph2vec_input_dir = output_location + "/graph2vec_input/"
    os.makedirs(graph2vec_input_dir, exist_ok=True)

    print("Save the graph2vec input into a file for each datapoint:")

    for index, row in graphs.iteritems():
        print("Current Iteration: "+str(index))
        with open(graph2vec_input_dir + str(index) + ".json", 'w') as f:
            f.write(row)

    print("`-> Done.")

    return graph2vec_input_dir


def run_graph2vec(input_dir, output_location, num_graph2vec_workers=1):
    print("Runs graph2vec on each of the above datapoints")
    subprocess.run([
        "python3",
        "/graph2vec/src/graph2vec.py",
        "--workers",
        str(num_graph2vec_workers),
        "--input-path",
        input_dir,
        "--output-path",
        output_location,
    ])
    print("`-> Done.")


if __name__=="__main__":
    juliet = pd.read_csv("../data/juliet.csv.zip")

    example = juliet.iloc[0]
    preprocessed_example = convert_to_graph2vec(example)

    print("# Welcome ---------------------------------- #\n"
          "Loaded in the first datapoint from juliet, and \n"
          "preprocessed it for the baseline model. The \n "
          "original is named 'example' and the output is \n"
          "named 'preprocessed_example'. \n"
          "Take a look!")
    import pdb; pdb.set_trace()

