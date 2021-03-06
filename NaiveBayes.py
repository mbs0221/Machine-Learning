import numpy as np
import re
import random
import feedparser as fd
import operator as op


def loadRawDataSet():
    sentences = [
        "my dog has flea problems help please",
        "maybe not take him to dog park stupid",
        "my dalmation is so cute I love him",
        "stop posting stupid worthless garbage",
        "mr licks ate my steak how to stop him",
        "qiut buying worthless dog food stupid"
    ]
    classVec = [0, 1, 0, 1, 0, 1]
    postingList = []

    for sentence in sentences:
        words = sentence.split(' ')
        postingList.append(words)

    return postingList, classVec


def loadDataSet(files):
    postList = []
    labels = []
    for file in files:
        text = open(file)
        lines = text.readlines()
        post = []
        for line in lines:
            words = re.findall("[a-zA-Z0-9]+", line)
            for word in words:
                post.append(word)
        postList.append(post)

    return postList


def createVocabList(dataset):
    """
    create a vocabulary

    :param dataset:
    :return:
    """

    vocabSet = set([])
    for document in dataset:
        vocabSet = vocabSet | set(document)

    return list(vocabSet)


def setOfWords2Vec(vocabList, inputSet):
    """
    set of words modal

    :param vocabList: vocabulary
    :param inputSet: a sentence
    :return:
    """
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] = 1
        else:
            print("the word: %s is not in my Vocabulary!" % (word))

    return returnVec


def bagOfWords2Vec(vocabList, inputSet):
    """
    bag of words modal

    :param vocabList: vocabulary
    :param inputSet: a sentence
    :return:
    """
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index] += 1

    return returnVec


def trainNaiveBayes(trainMatrix, trainCategory):
    """
    naive bayes training

    :param trainMatrix:
    :param trainCategory:
    :return:
    """
    numTrainDocs = len(trainMatrix)
    numWords = len(trainMatrix[0])
    pAbusive = sum(trainCategory) / float(numTrainDocs)
    # initialize possibility
    p0Num, p1Num = np.ones(numWords), np.ones(numWords)
    p0Denom, p1Denum = 2.0, 2.0

    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]
            p1Denum += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])

    p1Vect = np.log(p1Num / p1Denum)
    p0Vect = np.log(p0Num / p0Denom)

    return p0Vect, p1Vect, pAbusive


def classifyNB(vec2classify, p0v, p1v, pClass1):
    """
    nave bayes classifier

    :param vec2classify:
    :param p0v:
    :param p1v:
    :param pClass1:
    :return:
    """
    p1 = sum(vec2classify * p1v) + np.log(pClass1)
    p0 = sum(vec2classify * p0v) + np.log(1.0 - pClass1)

    if p1 > p0:
        return 1
    else:
        return 0


def testingNB():
    """
    test for naive bayes classifier

    :return:
    """
    data, labels = loadRawDataSet()
    vocabList = createVocabList(data)
    trainMatrix = []
    for post in data:
        trainMatrix.append(setOfWords2Vec(vocabList, post))

    p0v, p1v, pAb = trainNaiveBayes(trainMatrix, labels)
    testEntries = [
        "love my dalmation",
        "my stupid dog",
    ]
    for testEntry in testEntries:
        data = testEntry.split(' ')
        vec = setOfWords2Vec(vocabList, data)
        print("test entry classified as: ", classifyNB(vec, p0v, p1v, pAb))


def textParse(bigString):
    """
    text parser

    :param bigString:
    :return:
    """
    tokens = re.split('\W+', bigString)
    return [tok.lower() for tok in tokens if len(tok) > 2]


def spamTest():
    """
    test our naive bayes classifier on spam email
    :return:
    """

    docList = []
    classList = []
    fullText = []
    for i in range(1, 26):
        wordList = textParse(bigString=open('email/spam/%d.txt'%(i)).read())
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(1)
        wordList = textParse(bigString=open('email/ham/%d.txt'%(i)).read())
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(0)

    vocabList = createVocabList(docList)
    trainingSet = range(50)
    testSet = []
    for i in range(10):
        randIndex = int(random.uniform(0, len(trainingSet)))
        testSet.append(trainingSet[randIndex])
        del (trainingSet[randIndex])
    train, labels = [], []
    for docIndex in trainingSet:
        train.append(setOfWords2Vec(vocabList, docList[docIndex]))
        labels.append(classList[docIndex])

    p0v, p1v, pSpam = trainNaiveBayes(train, labels)
    errorCount = 0
    for docIndex in testSet:
        wordVec = setOfWords2Vec(vocabList, docList[docIndex])
        if classifyNB(wordVec, p0v, p1v, pSpam) != classList[docIndex]:
            errorCount += 1

    print("The error rate is: %d"%(float(errorCount)/len(testSet)))


def calcMostFreq(vocabList, fullText):
    """
    return top-30 words with most frequency

    :param vocabList:
    :param fullText:
    :return:
    """

    freqDict = {}
    for token in vocabList:
        freqDict[token] = fullText.count(token)
    sortedFreq = sorted(freqDict.iteritems(), key=op.itemgetter(1), reverse=True)

    return sortedFreq[:30]


def localWords(feeds):

    docList = []
    fullText = []
    for feed in feeds:
        for entry in feed['entries']:
            wordList = textParse(entry['summary'])
            docList.append(wordList)
            fullText.extend(wordList)

    vocabList = createVocabList(docList)
    top30Words = calcMostFreq(vocabList, fullText)

    for pair in top30Words:
        if pair[0] in vocabList:
            vocabList.remove(pair[0])

    """
    TODO:
    """