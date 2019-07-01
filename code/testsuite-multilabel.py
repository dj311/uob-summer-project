def test(data_path, model_name):

	import preprocess_code
	preprocess_code.code2vec(data_path)

#Need to write in something in case above fails

# baseline models are called 'baseline-model-multilabel' and 'baseline-model-binary'

	import pickle
	import keras
	import tensorflow
	infile = open('../data/' + model_name, 'rb')
	model_tsuite = pickle.load(infile)
	infile.close()
	
	import pandas as pd
	import numpy as np
	dataset = pd.read_csv(data_path)
	y_tsuite = dataset.iloc[:,6:]

	x_tsuite = pd.read_csv('../data/graphembeddings.csv')
	x_tsuite = x_tsuite.drop(columns = 'type')
	y_pred_tsuite = model.predict(x_tsuite)

	accuracy = model.evaluate(x_tsuite, y_tsuite)
	if accuracy > 0.7:
		say = 'Wahoo'
	else:
		say = 'Oh deary me'
	print('The accuracy is' + str(accuracy) + say)
