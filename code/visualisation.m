% Read data
label_str = readtable('/Users/xihajun/Documents/SummerProject/uob-summer-project/data/label.csv');
label = readtable('/Users/xihajun/Documents/SummerProject/uob-summer-project/data/visualisation.csv');
label = label{:,:};

% Plot scatters
figure
gscatter(label(:,1), label(:,2),label_str{:,2});
title("True label")

figure
gscatter(label(:,1), label(:,2),label(:,3));
title("Neural label")

figure
gscatter(label(:,1), label(:,2),label(:,4));
title("1NN label")

figure
gscatter(label(:,1), label(:,2),label(:,5));
title("3NN label")

figure
gscatter(label(:,1), label(:,2),label(:,7));
title("NB label")

figure
gscatter(label(:,1), label(:,2),label(:,8));
title("SVM label")
