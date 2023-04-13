import nltk
from matplotlib import pyplot as plt
from nltk.tokenize import sent_tokenize
import re
from nltk.corpus import stopwords
import numpy as np
import os
from typing import List
import networkx as nx
from numpy.linalg import norm

if not nltk.download('punkt'):
    nltk.download('punkt')
    print('punkt downloaded')
if not nltk.download('stopwords'):
    nltk.download('stopwords')
    print('stopwords downloaded')

def glove()->dict:
    """_summary_ : This function returns a dictionary with the word embeddings from the glove vectors file.

    Returns:
        dict: dictionary with the word embeddings from the glove vectors file. Glove embeddings are 100-dimensional vectors.
        The file is named glove.6B.100d.txt and it is present in the current directory.
    """
    word_embeddings = {}
    # path to the glove vectors file
    path_to_glove = os.path.join(os.path.dirname(__file__), 'glove.6B.100d.txt')
    # check if the file with glove vectors is present
    if not os.path.isfile(path_to_glove):
        print('glove.6B.100d.txt is not present in the current directory')
        print('Please download the file from httsps://nlp.stanford.edu/projects/glove/')
        return word_embeddings
    with open(path_to_glove, encoding='utf-8') as f:
        for line in f:
            values = line.split()
            word = values[0]
            vec = np.array(values[1:], dtype='float32')
            word_embeddings[word] = vec
    return word_embeddings

def remove_stopwords(sentence: str)-> str:
    """ _summary_ : This function removes the stopwords from the given sentence.
                    Stopwords are words that do not add any meaning to the sentence.
                    The nltk library is used to get the stopwords.
    Args:
        sentence (str): sentence from which the stopwords will be removed

    Returns:
        str: sentence without stopwords
    """
    # get the stopwords from the nltk library
    stop_words = set(stopwords.words('english'))
    words = sentence.split()
    cleaned_sentence = [w for w in words if w not in stop_words]
    return ' '.join(cleaned_sentence)

def preprocess_text(text:str)->List[str]:
    """ _summary_ : This function preprocesses the text. It tokenizes the text into sentences,
                    removes the punctuation, numbers, and special characters from the sentences,
                    and calls the remove_stopwords function to remove the stopwords from the sentences.
                    The returned list contains the sentences without stopwords.

    Args:
        text (str): String containing the text to be preprocessed.

    Returns:
        List[str]: The returned list contains the sentences without stopwords, punctuation, numbers, and special characters.
                   Each sentence is a string in the list.
    """
    # Tokenize the article into sentences
    sentences = sent_tokenize(text)
    # Cleaning the sentences from punctuation, numbers, and special characters using regex
    clean_sentences = [re.sub(r'[^A-Za-z]+', ' ', sentence) for sentence in sentences]
    clean_sentences = [s.lower() for s in clean_sentences]
    # Removing stopwords from the sentences
    clean_sentences = [remove_stopwords(sentence) for sentence in clean_sentences]
    return clean_sentences

def cosine_similarity(v1:np.ndarray, v2:np.ndarray)->float:
    """_summary_ : This function calculates the cosine similarity between two vectors.

    Args:
        v1 (np.ndarray): The first vector for which the cosine similarity will be calculated.
        v2 (np.ndarray): The second vector for which the cosine similarity will be calculated.

    Returns:
        _type_: The cosine similarity between the two vectors. The cosine similarity is a number between -1 and 1.
                The closer the number is to 1, the more similar the two vectors are. The closer the number is to -1,
                the more dissimilar the two vectors are. If the cosine similarity is 0, the two vectors are orthogonal.
                The returned value is a float.
    """
    return np.dot(v1, v2) / (norm(v1) * norm(v2))

def sentence_vectors(sentences_list:List[str])->List[np.ndarray]:
    """_summary_ : This function calculates the sentence vectors for the sentences in the sentences_list.
                   The sentence vectors are calculated by taking the average of the word embeddings for each word in the sentence.
                   The word embeddings are taken from the glove vectors file. The glove vectors file is present in the current directory.

    Args:
        sentences_list (List[str]): The list of sentences for which the sentence vectors will be calculated. 
                                    Each sentence is a string in the list. The sentences should be preprocessed.

    Returns:
        List[np.ndarray]: The returned list contains the sentence vectors. Each sentence vector is a numpy array of shape (100,).
    """
    word_embeddings = glove()
    sentence_vectors = []
    for sentence in sentences_list:
        if not sentence:
            continue
        splited_sentence = sentence.split()
        len_of_sentence = len(splited_sentence)
        # Initialize the sum of the word embeddings to vector of zeros
        # of the same dimension as the word embeddings.
        suma = np.zeros(100, dtype= 'float32')
        for word in splited_sentence:
            word_vec = word_embeddings.get(word)
            if word_vec is None: 
                continue
            suma += word_vec
        sentence_vectors.append(suma/len_of_sentence)
    return sentence_vectors

def get_similarity_matrix(sentence_vectors: List[np.ndarray])->np.ndarray:
    """_summary_ : This function calculates the similarity matrix for the sentence vectors.

    Args:
        sentence_vectors (List[np.ndarray]): The sentence vectors for which the similarity matrix will be calculated.

    Returns:
        np.ndarray: The similarity matrix. The similarity matrix is a numpy array of shape (n, n), where n is the number of sentences.
    """
    sim_mat = np.zeros([len(sentence_vectors),len(sentence_vectors)])
    for i in range(len(sentence_vectors)):
        for j in range(len(sentence_vectors)):
            if i != j:
                sim_mat[i][j] = cosine_similarity(sentence_vectors[i], sentence_vectors[j])
            else:
                sim_mat[i][j] = 1
    return sim_mat

def get_summary(text:str, n_of_sentences:int = 5)->str:
    """_summary_ : This function returns the summary of the text. The summary is a string containing 
                   the first n_of_sentences sentences of the text with the highest scores. The scores are calculated
                   using the PageRank algorithm.

    Args:
        text (str): The text for which the summary will be calculated.
        n_of_sentences (int, optional): Number of sentences in the summary. Defaults to 5.

    Returns:
        str: The summary of the text with the given number of sentences as n_of_sentences.
    """
    # Preprocess the text
    clean_sentences = preprocess_text(text)
    # Get the sentence vectors
    sentence_vector = sentence_vectors(clean_sentences)
    # Get the similarity matrix
    sim_mat = get_similarity_matrix(sentence_vector)
    # Create the graph
    G = nx.to_networkx_graph(sim_mat)
    # Get the scores for each sentence
    page_rank = nx.pagerank(G)
    # Sort the scores
    sorted_page_rank = {k: v for k, v in sorted(page_rank.items(), key=lambda item: item[1], reverse = True)}
    sorted_page_rank_indexes = list(sorted_page_rank.keys())
    summary = [sentence for index, sentence in enumerate(sent_tokenize(text)) if  index in sorted_page_rank_indexes[:n_of_sentences]]
    return ' '.join(summary)

if __name__ == "__main__":
    """_summary_ : This is the main function. It asks the user to enter the text for which he wants to get the summary.
                   It also asks the user to enter the number of sentences he wants in the summary.
    """
    print('Enter the text for which you want to get the summary:')
    text = input()
    print('Enter the number of sentences you want in the summary:')
    n_of_sentences = int(input())
    summary = get_summary(text, n_of_sentences)
    print('Summary:')
    print(summary)
