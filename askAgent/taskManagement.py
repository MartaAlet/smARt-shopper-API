import pymongo
import re
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from word2number import w2n

class TaskManager:
    def __init__(self, string):
        self.string = string
        #self.products_df = pd.read_csv('https://raw.githubusercontent.com/MartaAlet/smARt-shopper-API/main/objectsUpload.csv?token=GHSAT0AAAAAACR3CEGKJZUPXQ66ZTYTXNZIZRXCLMA', sep=';')
        #self.products = products_df[list(products_df.columns)[0]].values#['objectName'].values
        #self.debug = self.products_df.columns
        client = pymongo.MongoClient("mongodb+srv://ECVuser:rrpZTW6tZh6LvgBg@clusterecv.8ubs7wd.mongodb.net/?retryWrites=true&w=majority&appName=ClusterECV")
        db = client["smARt-shopper"]
        collection = db["objects"]
        self.products= [doc['objectName'] for doc in collection.find({}, {'objectName': 1}) if 'objectName' in doc]

    def perform_task(self):
        trans = self.string
        #return str(self.debug)
        task_info = ['no task', '##ERROR##'] # Initialize variables to store task information
        
        if 'order' in trans and not 'list' in trans:
            
            pattern_order_id = r'\d+'
            
            # Extract order id from transcription
            order_id_transc = self.extract_substring(trans, pattern_order_id)

            try:
                # Convert the word to a number
                orderID = str(w2n.word_to_num(order_id_transc))
            except ValueError:
                orderID = order_id_transc
            task_info = ['task 1', orderID]
            
        elif 'stock' in trans:
            pattern_product_stock = r'(?<=stock of\s).*'
            
            # Extract product name from transcription
            product_stock_transc = self.extract_substring(trans, pattern_product_stock)
            
            
            task_info = ['task 2', self.calculate_similarity_and_return_similars(self.products , product_stock_transc)]
            
        elif 'location' in trans:
            pattern_product_location = r'(?<=location of\s).*'
            
            # Extract product name from transcription
            product_location_transc = self.extract_substring(trans, pattern_product_location)
            
            
            
            task_info = ['task 3', self.calculate_similarity_and_return_similars(self.products , product_location_transc)]
            
        elif 'list' in trans and 'orders' in trans:
            task_info = ['task 4', '']
        
        return task_info
    
    def extract_substring(self, text, pattern):

        # Search for the pattern in the text
        match = re.search(pattern, text)

        if match:
            # Extract the product name from the matched group
            product_name = match.group()
            return product_name
        else:
            # Return empty string if no match found
            return '##ERROR##'

    # Get top 5 similars

    def top_five_key_value_pairs(self, input_dict):
        # Sort the dictionary items by values in descending order
        sorted_items = sorted(input_dict.items(), key=lambda item: item[1], reverse=True)
        
        # Take the first three key-value pairs
        top_five_pairs = sorted_items[:5]
        
        # Convert the key-value pairs to a dictionary
        result_dict = dict(top_five_pairs)
        
        return result_dict

    # Get more similars given a thereshold

    def get_most_similars(self, dictionary, thereshold):
        highest_value = max(dictionary.values())
        filtered_dict = {key: value for key, value in dictionary.items() if highest_value - value <= thereshold}
        return filtered_dict

    #-----------
    # SIMILARITY COMPUTATIONS

    # Compute cosine similarity between database item and transcription obtained
    def calculate_similarity_score(self, name, transcription):
        
        # Create a CountVectorizer object
        vectorizer = CountVectorizer()
        # Fit and transform the name and transcription into vectors
        
        vectors = vectorizer.fit_transform([name, transcription])
        # Compute the cosine similarity between the vectors
        similarity_score = cosine_similarity(vectors[0], vectors[1])[0][0]
        return similarity_score


    # Compute cosine similarity between each item and the transcription
    def calculate_similarity_and_return_similars(self, names, transcription):
        
        if transcription == '##ERROR##':
            return transcription
        
        else:
            similarity_dict = {}
            for name in names:
                similarity = self.calculate_similarity_score(name, transcription)
                similarity_dict[name] = similarity
                
                
            top5 = self.top_five_key_value_pairs(similarity_dict)
            
            most_similars = self.get_most_similars(top5, 0.2)
            
            return list(most_similars.keys())[0]#'##'.join(list(most_similars.keys()))
        