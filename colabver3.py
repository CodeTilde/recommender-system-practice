# Import Pandas
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np
from numpy import unique
from scipy.linalg import svd
from scipy.sparse.linalg import *
from sparsesvd import sparsesvd 
from scipy.sparse import csr_matrix
import scipy.sparse
def svdcompute (mat, k):
	UT, Sigma, VT = sparsesvd(mat,k)
	S=np.diag(Sigma)
	U = csr_matrix(np.transpose(UT), dtype=np.float32)
	S = csr_matrix(S, dtype=np.float32)
	VT = csr_matrix(VT, dtype=np.float32)
	return U, S, VT

# Load Movies Metadata
data = pd.read_csv('user_like_new.csv', low_memory=False)
data.head()
size = data.shape

media_id_vec= data['media_id'].unique()
user_id_vec = data['user_id'].unique()
# it is assumed the data set is sorted by time, if it is not the case, we do it at first step.  
# for every 4 liked media by each user, the latest is put in the test data. 
train_data_list = []
test_data_list = []
test_data=pd.DataFrame()
for user in user_id_vec:
	temp = data[data['user_id'] == user]
	n = len(temp)
	n_test = int(n/4)
	n_train = n-n_test
	train_data_list.append( temp.iloc[:n_train])
	if n_test>0:
		test_data_list.append( temp.iloc[n_train:n])
train_data = pd.concat(train_data_list)
test_data = pd.concat(test_data_list)
print (len (train_data))
print (len (test_data))
#media_id_un= train_data['media_id'].unique()
#user_id_un = train_data['user_id'].unique()

vals = [0  for i in range(len(user_id_vec))]
data = [ vals for i in range(len(media_id_vec))]
label_cols = [user for user in user_id_vec]
label_rows = [med_item for med_item in media_id_vec]
new_df = pd.DataFrame(data, label_rows, label_cols)
#producing item-user dataframe for item-based colabrative filtering
for i, user in enumerate (user_id_vec):#(new_df['user_id'].values):
	seq=train_data[train_data['user_id'] == user]['media_id']
	for item in seq:
		new_df.loc[item,user] = new_df.loc[item,user]+1
#producing user-item dataframe for user-based colabrative filtering 
vals = [0  for i in range(len(media_id_vec))]
data = [ vals for i in range(len(user_id_vec))]
label_cols = [media for media in media_id_vec]
label_rows = [user for user in user_id_vec]
usermedia_df = pd.DataFrame(data, label_rows, label_cols)
for i, user in enumerate (user_id_vec):#(new_df['user_id'].values):
	seq=train_data[train_data['user_id'] == user]['media_id']
	for item in seq:
		new_df.loc[item,user] = new_df.loc[item,user]+1

for user in user_id_vec:#(new_df['user_id'].values):
	seq=train_data[train_data['user_id'] == user]['media_id']
	for item in seq:
		usermedia_df.loc[user,item] = usermedia_df.loc[user,item]+1
# proceed by item-user dataframe
# convert the data frame to a sparse matrix
mat=scipy.sparse.csc_matrix(usermedia_df.values)
k = 50
U_red, Sigma_red, VT_red = svdcompute(mat, k)
# know we approximate  the binary user-item matrix by its K term SVD
USVT = U_red*(Sigma_red*VT_red)#np.dot(U_reds, VT_red)
df_USVT = pd.DataFrame(USVT)
aa=df_USVT.to_csv("USVT.csv")
th=.005
# theresholding to abtain a binary matrix 
usermedia_df_es= USVT > th*np.ones(USVT.shape)
size = usermedia_df_es.shape
count =0
for i in range(size[0]):
	for j in range (size[1]):
		if (usermedia_df_es[i,j]):
			count = count +1
			





error_sum =0
#size=usermedia_df_es.shape
error_sum = 0;
#len(test_data)
#producing the user-item matrix for test data 
vals = [0  for i in range(len(media_id_vec))]
data = [ vals for i in range(len(user_id_vec))]
label_cols = [media for media in media_id_vec]
label_rows = [user for user in user_id_vec]
usermedia_for_test = pd.DataFrame(data, label_rows, label_cols)

for user in user_id_vec:#(new_df['user_id'].values):
	seq=test_data[test_data['user_id'] == user]['media_id']
	for item in seq:
		usermedia_for_test.loc[user,item] = usermedia_for_test.loc[user,item]+1



#estimating error based on test data
error_sum =0
media_id_test= test_data['media_id'].unique()
user_id_test = test_data['user_id'].unique()
for user in user_id_test:#test_data['user_id'].values:
	seq=test_data[test_data['user_id'] == user]['media_id']
	user_index = np.where(user_id_vec==user)[0][0]
	for media in seq:
		med_index= np.where(media_id_vec==media)[0][0]
		if (usermedia_df_es[user_index,med_index]!=usermedia_for_test.loc[user,media]):
			error_sum +=1
error_sum_prim =0
for user, media in zip (test_data['user_id'].values, test_data['media_id'].values):
	user_index = np.where(user_id_vec==user)[0][0]
	med_index= np.where(media_id_vec==media)[0][0]
	if (not usermedia_df_es[user_index,med_index]):
			error_sum_prim +=1
#####################################################################################################

#media_id_test= test_data['media_id'].unique()
#user_id_test = test_data['user_id'].unique()
prod = np.multiply(usermedia_df_es, usermedia_for_test.to_numpy())
true_estimated_ones=np.sum(prod)
estimated_ones=usermedia_df_es.sum()
print ("true_estimated_ones", true_estimated_ones)
print ("total_estimated_ones", estimated_ones)
print ("estimated ones without train data", estimated_ones-len(train_data))








estimated_ones=0;
true_estimated_ones=0;
for user in user_id_test:
	for media in media_id_test:
		i = user_index= np.where(user_id_vec==user)[0][0]
		j = user_index= np.where(media_id_vec==media)[0][0]
		if (usermedia_df_es[i,j]):
			if (usermedia_df.loc[user,media]):
				pass
			else:						
				estimated_ones +=1
			if (usermedia_for_test.loc[user, media]):
				true_estimated_ones+=1
print(true_estimated_ones)
print(estimated_ones)
precision =true_estimated_ones/estimated_ones	
recall= true_estimated_ones/len(test_data)			
precision =true_estimated_ones/estimated_ones	
recall= true_estimated_ones/len(test_data)
print ("recall", recall)
print ("precision", precision)	

#Calculating  Recall
#Calculating Precision
#estimated_ones = 0
#true_estimated_ones=0
#count =0
#for k, user in enumerate (user_id_test):
#	for j , media in enumerate (media_id_vec):
#		i = user_index= np.where(user_id_vec==user)[0][0]
#		if (usermedia_df_es[i,j]):
#			if (usermedia_df.loc[user,media]):
#				pass
#			else:					
#				estimated_ones +=1
#			if (usermedia_for_test.loc[user, media]):
#				true_estimated_ones+=1

				
				
				
#print("true_estimated_ones", true_estimated_ones)				
#precision =true_estimated_ones/estimated_ones	
#recall= true_estimated_ones/len(test_data)					
#print("true_estimated_ones", true_estimated_ones)
#print("estimated_ones", estimated_ones)
#print (count)
#print ("recall", recall)
#print ("precision", precision)
#print (error_sum/len(test_data))
#print (error_sum_prim/len(test_data))
#estimating error based on test data +train data
#error_sum2=0
#for i, user in enumerate(user_id_vec):
#	for j, media in enumerate(media_id_vec):
				
#		if (usermedia_df_es[i,j]!=usermedia_for_test.loc[user,media]):
#			error_sum2 +=1	

#print (error_sum2/(len(test_data)+len (train_data)))


