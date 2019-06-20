"""

Module with utility functions for working with and preprocessing
source code.

"""

import json
import os
import snap
import subprocess
import swifter
import tempfile
import clang.cindex
import pandas as pd

from tqdm import tqdm

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


def process_for_graph2vec(datapoint):
    """
    Takes in a datapoint from juliet.csv.zip or vdisc_*.csv.gz (as
    loaded with pandas) and preprocesses it ready for the baseline
    model.
    """

    # Parse the source code with clang, and get out an ast:
    index = clang.cindex.Index.create()
    translation_unit = index.parse(
        path=datapoint.filename,
        unsaved_files=[(datapoint.filename, datapoint.code)],
    )
    ast_root = translation_unit.cursor

    # Memoise/concretise the ast so that we can consistently
    # modify it, then number each node in the tree uniquely.
    concretise_ast(ast_root)
    number_ast_nodes(ast_root)

    # Next, construct an edge list for the graph2vec input:
    edgelist = generate_edgelist(ast_root)

    # Construct a list of featurs for each node
    features = generate_features(ast_root)

    graph2vec_representation = {
        "edges": edgelist,
        "features": features,
    }

    return graph2vec_representation


def code2vec(csv_location):
    """
    Given a data set (e.g. juliet.csv.zip or vdisc_*.czv.gz) loaded in
    as a pandas dataframe, it applies the graph2vec embedding to the
    abstract syntax tree of each piece of source code. This is then
    output into the file "../data/graph_embeddings.csv".
    """
    print("Preprocess our code so it can be used as an input into graph2vec.")

    graphs = pd.Series()
    chunk_num = 1
    for chunk in pd.read_csv(csv_location, chunksize=1000):
        print("  - Processing chunk {}".format(chunk_num))

        processed_chunk = chunk.apply(process_for_graph2vec, axis='columns')
        processed_chunk.to_csv("../data/juliet_processed_for_graph2vec_chunk_{}.csv.gz".format(chunk_num))

        graphs.append(processed_chunk, ignore_index=True)

        chunk_num += 1
        print("    `-> Done.")

    print("`-> Done.")

    print("Dataset pre-processed for graph2vec. Saving to file:")
    graphs.to_csv("../data/juliet_processed_for_graph2vec.csv.gz")
    print("`-> Saved.")

    print("Making a temporary directory to put our graph2vec inputs into.")
    tmp_directory = tempfile.TemporaryDirectory()

    print("Save the graph2vec input into a file for each datapoint:")
    for index, row in tqdm(graphs.iteritems()):
        with open(tmp_directory.name + "/" + str(index) + ".json", 'w') as f:
            json.dump(row,f)
    print("`-> Done.")

    print("Runs graph2vec on each of the above datapoints")
    subprocess.run([
        "python3",
        "/graph2vec/src/graph2vec.py",
        "--input-path",
        tmp_directory.name + "/",
        "--output-path",
        "../data/graph_embeddings.csv",
    ])
    print("`-> Done.")

    # cleanup the temp directory
    tmp_directory.cleanup()


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

