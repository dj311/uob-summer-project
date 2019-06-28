% Read data
label_str = readtable('/Users/xihajun/Documents/SummerProject/uob-summer-project/data/label.csv');
label = readtable('/Users/xihajun/Documents/SummerProject/uob-summer-project/data/visualisation.csv');
label = label{:,:};
%label_s = char(label_str{:,2});
label_s = label_str{:,2};
true_label = []
a = {'CWE-191'}
b = {'CWE-191'}
for i = 1:length(label_s)
    if (isequal(label_s(i),a))||(isequal(label_s(i),b))
        true_label(i) = 1;
    else
        true_label(i) = 0;
    end
end
        
% Plot scatters
figure
gscatter(label(:,1), label(:,2),true_label);
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
