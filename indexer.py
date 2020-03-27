import json
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import OrderedDict, defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
import pickle


#from: https://scikit-learn.org/stable/modules/feature_extraction.html
class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

obj = {}
X = None
tokens = None
corpus = []
specialWordsDict = {}   #key = docPath, value = list of words in specialTags

def make_corpus():
    global corpus
    global specialWordsDict
    current = -1
    for key in list(obj.keys()):
        s = key.split('/')
        folder = int(s[0])
        if folder != current:
            current = folder
            print("current folder: " + str(current))
        #filenum = s[1]
        url = obj[key]
        
	    #the html from folder/filnum
        file_data = open( key, "rb")
        #parse html
        soup = BeautifulSoup(file_data, 'html.parser')
        words = soup.get_text()
        corpus.append(words) 
        #find all the specialWords in tags
        htmlTagContent = [str(j.extract().string).lower() for j in soup(['title', 'b', 'h1', 'h2', 'h3'])]
        specialWordsDict[key] = []
        for entireString in htmlTagContent:
            specialWordsDict[key].append(entireString)

    #writing the corpus to a text file
    f = open("corpus.txt", "w+")
    for e in corpus:
        for letter in e:
            try:
                f.write(letter)
            except:
                pass
        f.write("SPLIT_HERE_NOW\n")
    f.close()

    #writing the specialWordsDict to a json file
    file = open("specialWords.json", "w+")
    json.dump(specialWordsDict, file)
    file.close()

    print("corpus finished making")

def make_X():
    global X
    global tokens
    #read corpus.txt 
    corpus_file = open("corpus.txt", "r")
    corpus_content = corpus_file.read()
    corpus = corpus_content.split("SPLIT_HERE_NOW\n")
    print("finished reading corpus")

    #tokenize/remove stop words
    vectorizer = TfidfVectorizer(stop_words="english",min_df = 4, ngram_range=(1,2), analyzer = "word", tokenizer=LemmaTokenizer())
    X = vectorizer.fit_transform(corpus)
    tokens = vectorizer.get_feature_names()
    
    rows,cols = X.nonzero()


#reads the json and stores the html info in url_html_mapping
def make_file():
    url_html_map = {}

    obj_keys = obj.keys()  #has the actual folder/filenum mapped with docID from indexes
    obj_keys = list(obj_keys)

    #read specialWords.json
    with open("specialWords.json") as json_file:
        sp = json.load(json_file)
    specialWordsDict = dict(sp)
    
    #use the tokens to create a mapping for indexes
    output_dict = defaultdict(dict)
    rows,cols = X.nonzero()
    for i in range(0, len(X.data)):
        docID = int(rows[i])
        featureNameIndex = cols[i]
        word = tokens[featureNameIndex]
        #X.data[i] = tf-idf

        specialWord = 1
        #get doc path
        #u is (docID, tfidf) -> using docID-1 to index to the document in bookkeeping.json
        doc_path = obj_keys[docID-1]   #path to docID document
        for tagWords in specialWordsDict[doc_path]:
            if word in tagWords:
                specialWord = 0
        
        #changing tf-idf to use the HTML markup 
        if specialWord == 0:
            #X.data[i] = current tf-idf BEFORE changing
            X.data[i] += X.data[i]*0.3   #add 30% of current tf-idf if a specialWord

        output_dict[word][docID] = tuple((X.data[i], specialWord)) #(tf-idf, specialWordCheck)
        print("working on index " + str(i) + " of " + str(len(X.data)))

    #writing the indexes to a json file (our database)
    f = open("database.json", "w+")
    json.dump(output_dict, f)
    f.close()

    #printing for analytics
    print("Number of documents: ", len(obj))
    print("Number of unique words: ", len(output_dict))
    print("Size of Index on disk(KB): 104KB")
        
def analytics(query):
    global indexes
    print("got indexes")

    n = len(query.split(" "))
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2), analyzer = "word")
    
    query_vectorizer = vectorizer.fit_transform([query])
    feature_names = vectorizer.get_feature_names()
    
    sum_tfidf = 0
    for data in query_vectorizer.data:
        sum_tfidf += data
    #sum_tfidf = sum(query_vectorizer.data)
    obj_keys = list(obj.keys())

    #tf-idf(term in query)/sqrt(tf-idf(all terms in query added together)^2 + tf-df(document)^2) 
    
    cosSimArray = []
    for word in feature_names:
        if word in indexes.keys():
            index_document_dict = indexes[word]
            index  = feature_names.index(word)
            tfidf_word = query_vectorizer.data[index]
            weight = -1
            if word == query:
                weight = 0
            else:
                weight = 1
            for docId in index_document_dict.keys():
                tfidf_word_in_doc = index_document_dict[docId][0]
                
                #computing the cosine similarity
                cosSimVal = tfidf_word/(((sum_tfidf)**2 + (tfidf_word_in_doc)**2)**.5)
                
                #getting the url associated with docId 1137
                url = obj[obj_keys[int(docId)]]
                
                cosSimArray.append([tfidf_word_in_doc, cosSimVal, url, weight])

    #sort based on whether the link is relevant to the whole query or a certain part
    #get the top URLS associated with query; sort based on cosine similarity value; if there is a tie in cosine similairty, sort based on tfidf value
    final_urls = []
    for item in sorted(cosSimArray, key = lambda x:(x[3],-x[0],-x[1])):
        if item[2] not in final_urls:
            final_urls.append(item[2])
        
        if(len(final_urls) >= 20):
            break
    return final_urls
   
   
#LOAD NEEDED DATA
with open("webpages_raw/bookkeeping.json") as json_file:
    obj = json.load(json_file)
obj = OrderedDict(obj)

#read database.json for reading inverted index
with open("database.json") as json_file:
    indexes = json.load(json_file) 
indexes = OrderedDict(indexes)

    #make_corpus()
    #make_X()
    #make_file()
    #analytics("irvine")
print("finished loading everything!")


