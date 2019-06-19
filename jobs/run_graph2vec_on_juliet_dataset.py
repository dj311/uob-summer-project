import pandas as pd
from code.preprocess_code import code2vec

juliet = pd.read_csv("../data/juliet.csv.zip")
code2vec(juliet)

# will save output to ../data/graph_embeddings.csv


