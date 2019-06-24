def test(data_path, model_name):

	import preprocess_code
	preprocess_code.code2vec(data_path)
	import os.path
	if os.path.isfile('../data/graphembeddings.csv') == False:
		print('failed to vectorise data')

# baseline model is called 'baseline_model'

	infile = open(model_name, 'rb')
	model_tsuite = pickle.load(infile)
	infile.close()
	
	dataset = pd.read_csv(data_path)
	y_tsuite = dataset.iloc[:,6:]
	x_tsuite = pd.read_csv('../data/graphembeddings.csv')
	x_tsuite = x_tsuite.drop(columns = 'type')
	y_pred_tsuite = model.predict(x_tsuite)
	
	accuracy = model.evaluate(x_tsuite, y_tsuite)
	if accuracy > 0.7:
		say = 'Wahoo'
	else
		say = 'Oh deary me'
	print('The accuracy is' + str(accuracy) + say '
