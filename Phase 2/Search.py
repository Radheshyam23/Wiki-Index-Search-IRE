# Given a query, present a list of documents, ranked.
# Also handle field queries.

from collections import defaultdict
from operator import truediv
from sys import argv
import re
from math import log2

from time import time

from nltk.corpus import stopwords
# import nltk
# nltk.download('stopwords')
from nltk.stem import SnowballStemmer


# from Indexer import BagOfWords

class BagOfWords():

    def __init__(self):
        self.StopWords = set(stopwords.words("english"))
        self.StopWordsDict = defaultdict(int)
        for stop in self.StopWords:
            self.StopWordsDict[stop] = 1
        # Add custom stopwords in this list
        MoreStopWords = []
        for stop in MoreStopWords:
            self.StopWordsDict[stop] = 1
        self.SnowStem = SnowballStemmer('english')

    def Tokenize(self,unrefinedStr):

        # Otherwise some characters are incorrectly converting to japanese/chinese type characters.
        unrefinedStr = unrefinedStr.encode("ascii", errors="ignore").decode()
        unrefinedStr = re.sub(r'http[^\ ]*\ ', r' ', unrefinedStr) # removing urls
        # unrefinedStr = re.sub(r'\S+\.com\S+',' ', unrefinedStr) # removing urls
        # unrefinedStr = re.sub(r'\—|\'|\`|\‘|\′|\"|\”|\“|\″|\–|\−|\·|\||\.|\*|\[|\{|\}|\(|\)|\]|\;|\:|\,|\=|\＝|\-|\+|\_|\!|\?|\/|\>|\＜|\＜|\<|\&|\\|\#|\$|\@|\%||\₹|\₽|\€|\n', r' ', unrefinedStr) # removing special characters
        unrefinedStr = re.sub(r'\—|\'|\`|\"|\||\.|\*|\[|\{|\}|\(|\)|\]|\;|\:|\,|\=|\~|\-|\+|\_|\!|\?|\/|\>|\<|\&|\\|\#|\$|\@|\%|\n', r' ', unrefinedStr)
        
        unrefinedStr = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', unrefinedStr) # removing html entities

        # To Do:
        # Remove prefixes, suffixes to numbers like 100th 25kmph

        return unrefinedStr.split()

    def StopANDStem(self, Bag):
        Bag = [self.SnowStem.stem(word) for word in Bag if self.StopWordsDict[word] != 1]

        # To DO:
        # Probably remove long numbers
        # Remove 1 letter words

        return Bag


FieldScoreCard = {
    't':10,
    'i': 5,
    'b': 1,
    'c': 5,
    'l': 2,
    'r': 2
}

PostingsCache = {}

IDFcache = defaultdict(int)

def UpdateIDFcache(token, DocFreq):
    # IDF: log(N/df) (N = total number of documents, df = number of documents containing the token)

    if IDFcache[token] != 0:
        return
    
    IDFscore = log2(NumDocs / DocFreq)
    IDFcache[token] = IDFscore


# Field queries: title, infobox, body, category, links, references.

def ModifiedBinarySearch(SearchList, Token):
    # If the token is between any two consecutive elements, return the previous element
    Start = 0
    End = len(SearchList) - 1

    # if token > end?
    if Token > SearchList[End]:
        return End

    while Start <= End:
        Mid = (Start + End) // 2
        if Token >= SearchList[Mid] and Token < SearchList[Mid + 1]:
            return Mid
        elif Token < SearchList[Mid]:
            End = Mid
        else:
            Start = Mid + 1
    return -1

ScoresList = []

def NormalQuery(QueryString):
    global ScoresList
    # Not a field query
    # Step1: Tokenize the query
    BOW = BagOfWords()
    QueryTokens = BOW.Tokenize(QueryString)
    QueryTokens = BOW.StopANDStem(QueryTokens)
    QueryTokens = [token.lower() for token in QueryTokens]

#######
    # print("QueryTokens",QueryTokens)
#######

    QueryTF = defaultdict(list)

    # Step2: Get the postings list for each token
    # Do binary search on secondary index for my token
    for tokens in QueryTokens:
        TFscore = CalcTF(tokens,'z')    # Taking z to indicate not a field query
        if len(TFscore) != 0:
            QueryTF[tokens] = TFscore

    # print("QueryTF",QueryTF)
    # print()

    for tokens in QueryTF.keys():
        for entries in QueryTF[tokens]:
            ScoresList.append((entries[0],entries[1]*IDFcache[tokens]))

    # print("ScoresList",ScoresList)
    # print()

# Do for field query too

def FieldQuery(QueryString):
    global ScoresList

    # [b:Marc, Spector, i:Marvel, Comics, c:1980, comics, debuts]

    #step 1: Split query into fields
    # step2; tokenise the fields
    QueryTokens = defaultdict(list)

    SplitQuery = QueryString.split(' ')
    # b:Marc Spector i:Marvel Comics c:1980 comics debuts

    for entity in SplitQuery:
        if len(entity.split(":")) == 2:
            currTok = entity.split(":")[0]
            QueryTokens[currTok].append(entity.split(":")[1])
        else:
            QueryTokens[currTok].append(entity)


    QueryTF = defaultdict(list)
    
    for fields in QueryTokens.keys():
        BOW = BagOfWords()
        QueryTokens[fields] = BOW.Tokenize(' '.join(QueryTokens[fields]))
        QueryTokens[fields] = BOW.StopANDStem(QueryTokens[fields])
        QueryTokens[fields] = [token.lower() for token in QueryTokens[fields]]

        # print("QueryTokens",QueryTokens)
    
        for tokens in QueryTokens[fields]:
            TFscore = CalcTF(tokens,fields)
            if len(TFscore) != 0:
                if tokens in QueryTF.keys():
                    QueryTF[tokens].extend(TFscore) 
                else:
                    QueryTF[tokens] = TFscore

    for tokens in QueryTF.keys():
        for entries in QueryTF[tokens]:
            ScoresList.append((entries[0],entries[1]*IDFcache[tokens]))
 

def CalcTF(tokens, isField):
    #####
    # print("token for TF:",tokens)
    #####

    if tokens in PostingsCache.keys():
        Posting = PostingsCache[tokens]
        # print("Posting present in cache: ",Posting)
    
    else:
        Index = ModifiedBinarySearch(SecondaryIndexList, tokens)
        # print("Index for token:",Index)
        if Index == -1:
            return []
        
        # Get the postings list
        IndexFileName = InvertedIndexPath +'/index' + str(Index) + '.txt'
        PostingsListFile = open(IndexFileName, 'r')
        PostLines = PostingsListFile.readlines()
        PostingsListFile.close()

        Posting = ""

        for line in PostLines:
            if line.split(':')[0] == tokens:
                Posting = line.split(':')[1]
                Posting = Posting.strip("\n").strip(" ")
                PostingsCache[tokens] = Posting
                break
        if Posting == "":
            return []

    # print("The Posting is:"+Posting)
        
    # Now parse the Posting and calculate the score for every document (TF score)
    # Basically how frequently does this token appear in that particular document


    TokenTFscores = []

    # First split into individual docs
    DocPosting = list(filter(None,Posting.split('d')))

    # print("DocPosting",DocPosting)

    NumDocs = len(DocPosting)
    UpdateIDFcache(tokens, NumDocs)
    
    for doc in DocPosting:
        num = re.findall(r'\d+', doc)
        fields = re.findall(r'[a-z]+', doc)

# #########
#         print(num)
#         print(fields)
# #########
        DocID = int(num[0])

        TFscore = 0

        if isField == 'z':
            for i in range(len(fields)):
                TFscore += FieldScoreCard[fields[i]] * int(num[i + 1])

        else:
            for i in range(len(fields)):
                if fields[i] == isField:
                    TFscore += FieldScoreCard[fields[i]] * int(num[i + 1])

        TokenTFscores.append((DocID, TFscore))

    return TokenTFscores

    # TF can also be divided by the total number of tokens in the document (leaving for later)
    # However while dividing, if the document is very huge, score will become very small so we can keep a threshold and all...

def CheckField(QueryString):

    neverEntered = True

    temp = QueryString.split(' ')
    for i in temp:
        if len(i.split(':')) != 1:
            neverEntered = False
            if i.split(':')[0] not in FieldScoreCard.keys():
                return False

    if neverEntered == True:
        return False
    else:
        return True


    # print("Field Check:",newArr)

    # if len(newArr) == 1:
    #     return False
    # for i in range(0,len(newArr),2):
    #     if newArr[i] not in FieldScoreCard.keys():
    #         return False
    # return True
    
    # b:Marc Spector i:Marvel Comics c:1980 comics debuts
    # [b:Marc, Spector, i:Marvel, Comics, c:1980, comics, debuts]



def PrintDocName(docNum):
    global DocChunk
    TitlePageNum = docNum//DocChunk
    TitleLineNum = docNum%DocChunk

    # print("TitlePageNum",TitlePageNum,"TitleLineNum",TitleLineNum)

    FileName = InvertedIndexPath+'/title'+str(TitlePageNum)+'.txt'
    TitlePageFile = open(FileName, 'r')
    for i in range(TitleLineNum):
        TitlePageFile.readline()
    DocName = TitlePageFile.readline().strip('\n')
    TitlePageFile.close()
    print(DocName)


def GetRanking():
    global ScoresList
    ScoresList.sort(key = lambda x: x[1], reverse = True)
    PageRank = [rank[0] for rank in ScoresList]
    
    # print()
    # print("RESULTS!!!!:")
    # print()

    count = 0
    for docNum in PageRank:
        PrintDocName(docNum)
        count +=1
        if count == 10:
            break
    # print("----------------------------------------------------")


#######################
# Running



# Arguments passed: <path_to_inverted_index> <query_string>
InvertedIndexPath = "./data"
# QueryFilePath = argv[2]
# QueryString = argv[2]
# Assuming a query document instead.
QueryDoc = open('./SampleQs/queries.txt','r')
QueryString = QueryDoc.readlines()   
QueryDoc.close()         
            

# Getting the Secondary Index tokens
SecondaryFileAddr = InvertedIndexPath + '/SecondaryIndex.txt'
SecondaryIndex = open(SecondaryFileAddr, 'r')
SecondaryIndexList = SecondaryIndex.readline().split(' ')
SecondaryIndex.close()

# Whats the number of documents in the dump?
ExtraDets = open('./data/extraDets.txt', 'r')
# NumDocs = int(ExtraDets.readlines().split(':')[1])
Dets = ExtraDets.readlines()
NumDocs = int(Dets[0].split(':')[1])
DocChunk = int(Dets[1].split(':')[1])
TokenChunk = int(Dets[2].split(':')[1])
ExtraDets.close()

for line in QueryString:
    startTime = time()
    isField = CheckField(line)
    # print("Query:",line,"isField:",isField)
    ScoresList = []
    if isField:
        FieldQuery(line)
        GetRanking()
    else:
        NormalQuery(line)
        GetRanking()
    EndTime = time()
    print(EndTime-startTime)
    print()

