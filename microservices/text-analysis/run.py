#Tutorial 4: Visualising with classical machine learning algorithms! 
#author: Dr Mahmoud El-Haj (with help from the Internet) as part of the "Visualise My Corpus Tutorial" an event by Lanacaster University's UCREL and DSG Seminars
#GitHub repository: https://github.com/drelhaj/NLP_ML_Visualization_Tutorial

#The task is to classify talks and abstracts into their years (or year spans). 
# For example a talk titled "Systems security" belongs to year 1999 or to the 1990s span.
#We go a step forward by showing you how to create noun-clouds and verb-clouds using SpaCy.
#Our data-set is a list of talks and abstracts from the CCC conference https://gitlab.com/maxigas/cccongresstalks/
import re
from nltk.corpus import stopwords
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn import svm
from sklearn.linear_model import LogisticRegression

import warnings
warnings.filterwarnings("ignore")
import glob
import pandas as pd
from os import listdir
from os.path import isfile, join
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
import matplotlib.pyplot as plt
import seaborn as sns
import mglearn
from sklearn.feature_extraction.text import CountVectorizer
# Input data files are available in the "../csvs/" directory.
#Our data-set is a list of talks and abstracts from the CCC conference https://gitlab.com/maxigas/cccongresstalks/

if __name__ == '__main__':

    directory = "csvs/"
    combinedFile = "csvs/combined_csv.csv"

    combinedSpanFile = "csvs/combined_span_csv.csv"

    # delete csv combined-spans if it exists so it doesn't duplicate its contents (I later explain what this file is)
    if os.path.exists(combinedSpanFile):
        os.remove(combinedSpanFile)
        
    # delete csv combined if it exists so it doesn't duplicate its contents (I later explain what this file is)
    if os.path.exists(combinedFile):
        os.remove(combinedFile)

    #The following loops through the CSV files and shows how many talks (rows) are there in each year.
    for filename in os.listdir(directory):
        if filename.endswith(".csv"): 
            print(filename)
            df1 = pd.read_csv((directory+'/'+filename), delimiter='|', header=0, error_bad_lines=False)
            print('Number of titles: {:,}\n'.format(df1.shape[0]))
            continue
    #The following loops through all the CSVs (per year) in the CSV file and creates a combined file with data from all csvs into one.



    # delete csv combined if it exists so it doesn't duplicate its contents
    if os.path.exists(combinedFile):
        os.remove(combinedFile)
        
    extension = 'csv'
    #notice that the code changes the delimiter from "|" to "," which is the norm.
    all_filenames = [f for f in listdir(directory) if isfile(join(directory, f))]
    #combine all files in the list
    combined_csv = pd.concat([pd.read_csv((directory+'/'+f), delimiter='|', error_bad_lines=False).replace({',': ' '}, regex=False) for f in all_filenames ])
    #export to csv
    combined_csv.to_csv(combinedFile, index=False,encoding='utf-8-sig')

    #read the newly created combined file and show a sample of 10 rows (notice teh year column)
    df_years = pd.read_csv(combinedFile, delimiter=',', header=0, error_bad_lines=False)
    print('Number of titles: {:,}\n'.format(df_years.shape[0]))
    df_years.sample(10)
    #what the following code does is it plays with the years to make them look like a span of years.
    #The reason I do that to show you later that classifying text (titles or abstracts) into years will yield low accuracy results 
    #   as there are 35 years of talks
    # What I will do is group the years into a span of 1980s, 1990s, 2000s and 2010s(this includes years from 2010 and later)
    combinedSpanFile = "csvs/combined_span_csv.csv"

    # delete csv combined if it exists so it doesn't duplicate its contents
    if os.path.exists(combinedSpanFile):
        os.remove(combinedSpanFile)

    # here is a list of replace statements to convert years into year spans (i'm sure there is a better way to do this but this suffice :) 
    # we save the updated year combined file to a new file called "combined_span_csv.csv".
    with open(combinedFile, "rt", encoding="utf8") as fin:
        with open(combinedSpanFile, "wt", encoding="utf8") as fout:
            for line in fin:
                newString = re.sub("201\d{1}", "2010", line)
                newString = re.sub("200\d{1}", "2000", newString)
                newString = re.sub("198\d{1}", "1980", newString)
                newString = re.sub("199\d{1}", "1990", newString)
                fout.write(newString)
    #here I print a sample of 10 rows from the combined_span_csv.csv file.
    combinedSpanFile = "csvs/combined_span_csv.csv"

    df_span = pd.read_csv(combinedSpanFile, delimiter=',', header=0, error_bad_lines=False)
    print('Number of titles: {:,}\n'.format(df_span.shape[0]))
    df_span.sample(10)
    #This line changes the way the machine learning works
    #keepnig df as df_span will classify text into 4 classes 1980s,1990s,2000s,2010s
    #changing it to df_years will classify text into 35 classes which will of course result in lower scores.
    df = df_span

    #print(os.getcwd())
    plots = "plots"


    #thsi prints how many samples are tehre in the combined (or span) file.
    df.head()
    print('Number of titles: {:,}\n'.format(df.shape[0]))

    #we are only intersted in classifying the abstracts as they have more text than the titles. To change that replace abstract with title all over.
    from io import StringIO
    col = ['year', 'abstract'] #those are the two columns we are interested in bascially (label: Year, Text: abstract)
    df = df[col]
    #make sure we have no null abstracts to avoid any errors
    df = df[pd.notnull(df['abstract'])]
    df.columns = ['year', 'abstract']

    #create teh categories (labels) from the year column
    df['category_id'] = df['year'].factorize()[0]
    category_id_df = df[['year', 'category_id']].drop_duplicates().sort_values('category_id')
    category_to_id = dict(category_id_df.values)
    print(type(category_to_id))
    id_to_category = dict(category_id_df[['category_id', 'year']].values)
    df.head()

    #I'm only showing you the Support Vector Machines (SVM) and Naive Bayes (NB) classifiers, 
    #The implementation for Logistic Regression (LR) is in there you just need to add "LR" to the array below.
    modelsArray = ["SVM","NB","LR"]
    for w in range(len(modelsArray)):
        model_type = modelsArray[w]

        #prepare the training and testing dataset
        #This randomly splits our data into training and testing, here we choose to go with 0.30 (30%) for testing and the rest for training
        #X in our case is the text (abstract), Y is the labels (years)
        X_train, X_test, y_train, y_test = train_test_split(df['abstract'], df['year'],random_state = 1, test_size=0.30)
        
            
        #we use a bag of words approach, here we go with 1 ngram, if you want bigrams (2,2), unigrams and bigrams (1,2)...etc
        count_vect = CountVectorizer(analyzer='word', ngram_range=(1, 1))#ngram size, default 1,1, default word ngrams
        
        #you can use a tf, idf vectorizer which should do better than word frequency, I also show you how to remove stop words.
        #count_vect = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words = stopwords.words("english"), sublinear_tf=True)#ngram size, default 1,1, default word ngrams
        
        count_vect.fit(X_train)    
        #transforming data to be ready for analysis and machine learning
        #handling missing data, remove string formatting, convert categorical data to numerical ....etc
        X_train_tfidf = count_vect.transform(X_train)
        X_train_tfidf = count_vect.fit_transform(X_train)
        X_test_tfidf = count_vect.transform(X_test)
        
        #algorithms setup, you can change the C value for SVM
        if model_type=="SVM":
            clf = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto')
        if model_type=="NB":
            clf = MultinomialNB()
        if model_type=="LR":
            clf = LogisticRegression(random_state=0, solver='lbfgs',multi_class='multinomial', max_iter=4000)

        #train the model
        train_model=clf.fit(X_train_tfidf, y_train)
        #predicting years for testing data
        test_accuracy=train_model.predict(X_test_tfidf)
        #print training and testnig accuracy
        print("Training/Testing Accuracy" , '\t' , model_type , '\t' , train_model.score(X_train_tfidf, y_train) , '\t' , train_model.score(X_test_tfidf, y_test))

        #plot confusion matrices
        import seaborn as sns
        from sklearn.metrics import confusion_matrix
        
        conf_mat = confusion_matrix(y_test, test_accuracy)
        fig, ax = plt.subplots(figsize=(9,9))
        sns.heatmap(conf_mat, annot=True, fmt='d',cmap="RdBu_r",
                    xticklabels=category_id_df.year.values, yticklabels=category_id_df.year.values)
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        #plt.show(block=False)
        # pltFileName = plots+'/'+'combined'+'_'+model_type+'.pdf';
        # plt.savefig(pltFileName)
    