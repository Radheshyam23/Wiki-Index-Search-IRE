# After reading each page from the dump, we are going to process it and store it then and there, instead of getting all the files and then processing.

import sys
import xml.sax
import re       # Regex
from nltk.corpus import stopwords
# import nltk
# nltk.download('stopwords')
from collections import defaultdict
from nltk.stem import SnowballStemmer
import os

Storage = {"PageNum": 0, "IndexFileNum": 0, "PostingLists": defaultdict(list), "PageTitle": [], "DocChunk": 1001, "TokenChunk": 10001}

StopWordsExtension = ["jpg"]

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

class WikiHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        self.count = -1
        self.Title = ""
        self.Text = ""
        self.InfoBox = ""
        self.Body = ""
        self.Category = ""
        self.Links = ""
        self.References = ""

    def ResetData(self):
        self.Title = ""
        self.Text = ""
        self.InfoBox = ""
        self.Body = ""
        self.Category = ""
        self.Links = ""
        self.References = ""

    def startElement(self, name, attrs):
        self.Tag = name

    def characters(self, content):
        if self.Tag == "title":
            self.count += 1
            self.Title = content

        elif self.Tag == "text":
            self.Text += content

    def endElement(self, name):
        self.Tag = ""
        if name == "page":
            # Call the processing functions
            self.ProcessData()
            self.Indexing()
            # print("Page: ",Storage["PageNum"])
            self.ResetData()

    def ProcessData(self):
        # Clean Text and extract components

        # Remove newline
        self.Text = re.sub("\n"," ",self.Text)

        Storage["PageTitle"].append(self.Title)

        # Casefolding: Removing uppercase
        self.Title = self.Title.lower()
        self.Text = self.Text.lower()

        # Get Infobox
        self.GetInfobox()
            
        # Get References. This also gets Categories and External Links
        self.GetReferences()


        # Bag of Words
        BOW = BagOfWords()
        # Tokenise
        self.Title = BOW.Tokenize(self.Title)
        self.Body = BOW.Tokenize(self.Body)
        self.InfoBox = BOW.Tokenize(self.InfoBox)
        self.Category = BOW.Tokenize(self.Category)
        self.References = BOW.Tokenize(self.References)
        self.Links = BOW.Tokenize(self.Links)

        # Removing Stop words and Stemming
        self.Title = BOW.StopANDStem(self.Title)
        self.Body = BOW.StopANDStem(self.Body)
        self.InfoBox = BOW.StopANDStem(self.InfoBox)
        self.Category = BOW.StopANDStem(self.Category)
        self.References = BOW.StopANDStem(self.References)
        self.Links = BOW.StopANDStem(self.Links)
        
    def GetInfobox(self):
        # Getting the Infobox data
        self.InfoBox = ' '.join(re.findall("(?<={{infobox)(.*?)(?=}})",self.Text))
        # Removing Infobox data from the text.
        self.Text = re.sub("({{infobox)(.*?)(}})"," ",self.Text)
        # self.InfoBox = re.sub('[|=\[\]\{\}\(\)\'\"\,\*\.\;]',' ',self.InfoBox)
        # self.InfoBox = self.InfoBox.strip()

    def GetReferences(self):
        SplitText = self.Text.split("== references ==")
        if len(SplitText) == 1:
            # Because of inconsistencies in markup heading (space between = and text)
            SplitText = self.Text.split("==references==")
        self.Body = SplitText[0]

        if len(SplitText) != 1:
            # References section exists
            self.References = SplitText[1]
            self.GetCategories()
            self.GetExternalLinks()

        
        self.References = ' '.join(re.findall("(?<=\*\[)(.*?)(?=\])",self.References))
      
    def GetCategories(self):
        self.Category = ' '.join(re.findall("(?<=\[\[category:)(.*?)(?=\]\])",self.References))
        # Removing Categories from References
        self.References = re.sub("(\[\[category:)(.*?)(\]\])", " ", self.References)
    
    def GetExternalLinks(self):
        ExternalSplit = self.References.split("==external links==")
        if len(ExternalSplit) == 1:
            # Because of inconsistencies in markup heading (space between = and text)
            ExternalSplit = self.References.split("== external links ==")
        self.References = ExternalSplit[0]

        if len(ExternalSplit) != 1:
            # References section exists
            temp = ExternalSplit[1]
            self.Links = ' '.join(re.findall("(?<=\* \[)(.*?)(?=\])",temp))

    def Indexing(self):
        PageIndexer = Indexing(self.Title, self.InfoBox, self.Body, self.Category, self.References, self.Links)
        PageIndexer.CreateIndex()


    def endDocument(self):
        print("Document Ended!!!")

        # If anything is left unwritten!!!
        if len(Storage["PageTitle"]) != 0:
            writeIntoFile()
            Storage["IndexFileNum"] += 1

        # Write extra stats into anothe file called extraDets.txt
        ExtraFile = open('./data/extraDets.txt', 'w')
        DocDets = ["DocSize:" + str(Storage["PageNum"]),"DocChunk:"+str(Storage["DocChunk"]),"TokenChunk:"+str(Storage["TokenChunk"])+"\n"]
        ExtraFile.write('\n'.join(DocDets))
        ExtraFile.close()

class Indexing:
    def __init__(self, Title, Infobox, Body, Categories, References, ExtLink):
        self.Title = Title
        self.InfoBox = Infobox
        self.Body = Body
        self.Category = Categories
        self.Links = ExtLink
        self.References = References
    
    def CreateIndex(self):
        # Creating a Dictionary for each section and also maintaing a Dict for the whole page

        TokensDict = defaultdict(int)
        TitleDict = defaultdict(int)
        for token in self.Title:
            TokensDict[token] += 1
            TitleDict[token] += 1
        
        InfoDict = defaultdict(int)
        for token in self.InfoBox:
            TokensDict[token] += 1
            InfoDict[token] += 1

        BodyDict = defaultdict(int)
        for token in self.Body:
            TokensDict[token] += 1
            BodyDict[token] += 1

        CategoryDict = defaultdict(int)
        for token in self.Category:
            TokensDict[token] += 1
            CategoryDict[token] += 1

        RefDict = defaultdict(int)
        for token in self.References:
            TokensDict[token] += 1
            RefDict[token] += 1

        LinkDict = defaultdict(int)
        for token in self.Links:
            TokensDict[token] += 1
            LinkDict[token] += 1

        # Updating Posting List 
        for token in TokensDict.keys():
            PostListStr = 'd'+str(Storage["PageNum"])
            if TitleDict[token] != 0:
                PostListStr += 't'+str(TitleDict[token])
            if InfoDict[token]:
                PostListStr += 'i'+str(InfoDict[token])
            if BodyDict[token]:
                PostListStr += 'b'+str(BodyDict[token])
            if CategoryDict[token]:
                PostListStr += 'c'+str(CategoryDict[token])
            if RefDict[token]:
                PostListStr += 'r'+str(RefDict[token])
            if LinkDict[token]:
                PostListStr += 'l'+str(LinkDict[token])

            Storage["PostingLists"][token].append(PostListStr)

        Storage["PageNum"] += 1
        if Storage["PageNum"]%int(Storage["DocChunk"]) == 0:
            writeIntoFile()
            Storage["PostingLists"] = defaultdict(list)
            Storage["IndexFileNum"] += 1
            Storage["PageTitle"] = []


def writeIntoFile():
    FinalPostingList = ""
    for token in sorted(Storage["PostingLists"].keys()):
        TokenPostingList = token + ':'
        TokenPostingList += ''.join(Storage["PostingLists"][token])
        FinalPostingList += TokenPostingList +'\n'

    filename = './data/index' + str(Storage["IndexFileNum"]) + '.txt'
    os.makedirs(os.path.dirname(filename),exist_ok=True)
    IndexFile = open(filename, 'w')
    IndexFile.write(FinalPostingList)
    IndexFile.close()

    TitleFileName = './data/title' + str(Storage["IndexFileNum"]) + '.txt'
    os.makedirs(os.path.dirname(TitleFileName),exist_ok=True)
    TitleFile = open(TitleFileName, 'w')
    TitleStr = '\n'.join(Storage["PageTitle"])
    TitleFile.write(TitleStr)
    TitleFile.close()


def MergeFiles():
    tempFileNames = ['./data/temp0.txt','./data/temp1.txt']

    # Rename index0 to temp1.
    os.rename('./data/index0.txt','./data/temp1.txt')

    for i in range(1,Storage["IndexFileNum"]):
        readFileName = './data/index'+str(i)+'.txt'
        readFiles = [open(readFileName,'r'),open(tempFileNames[i%2],'r')]

        if os.path.exists(tempFileNames[(i+1)%2]):
            os.remove(tempFileNames[(i+1)%2])
        FinalIndexFile = open(tempFileNames[(i+1)%2],'w')
        
        line0 = readFiles[0].readline()
        line1 = readFiles[1].readline()
        splitLine0 = line0.split(':')
        splitLine1 = line1.split(':')
    
        while line0 and line1:
            if splitLine0[0] < splitLine1[0]:
            # Token of line1 lexicographically smaller than that of line 2
                FinalIndexFile.write(line0)
                line0 = readFiles[0].readline()
                splitLine0 = line0.split(':')
            
            elif splitLine0[0] > splitLine1[0]:
                FinalIndexFile.write(line1)
                line1 = readFiles[1].readline()
                splitLine1 = line1.split(':')

            else:
                FinalIndexFile.write(splitLine0[0]+':'+splitLine0[1].strip()+splitLine1[1])
                line0 = readFiles[0].readline()
                line1 = readFiles[1].readline()
                splitLine0 = line0.split(':')
                splitLine1 = line1.split(':')
        
        while line0:
            FinalIndexFile.write(line0)
            line0 = readFiles[0].readline()
        
        while line1:
            FinalIndexFile.write(line1)
            line1 = readFiles[1].readline()


        readFiles[0].close()
        readFiles[1].close()
        FinalIndexFile.close()

        # Delete old index file
        os.remove(readFileName)

    # Rename temp0 to BigIndex
    os.rename(tempFileNames[Storage["IndexFileNum"]%2],'./data/BigIndex.txt')
    os.remove(tempFileNames[(Storage["IndexFileNum"]+1)%2])

def FinalSplit():

    PageCount = 0

    BigIndex = open('./data/BigIndex.txt','r')
    line = BigIndex.readline()
    TokenCount = 1

    IndexPage = open('./data/index0.txt','w')

    SecondaryIndexList = []
    SecondaryIndexList.append(line.split(':')[0])

    writeList = []

    while line:
        if TokenCount%int(Storage["TokenChunk"]) == 0:

            IndexPage.write(''.join(writeList))
            IndexPage.close()
            PageCount += 1
            PageName = './data/index' + str(PageCount) + '.txt'
            IndexPage = open(PageName, 'w')
            writeList = []
            SecondaryIndexList.append(line.split(':')[0])
        
        writeList.append(line)
        line = BigIndex.readline()
        TokenCount += 1

    IndexPage.write(''.join(writeList))
    IndexPage.close()
    BigIndex.close()

    # Has the first token of each Indexfile for easier search
    SecondaryIndex = open('./data/SecondaryIndex.txt','w')
    SecondaryIndex.write(' '.join(SecondaryIndexList))
    SecondaryIndex.close()

    os.remove('./data/BigIndex.txt')

    print("Total Pages: ",PageCount)
    print("Total Tokens: ",TokenCount)

parser = xml.sax.make_parser()
parser.setContentHandler(WikiHandler())
# parser.parse("/home/radheshyam/Desktop/Year3_1/IREL/IREL-MiniProject/Phase 1/enwiki-20220720-pages-articles-multistream15.xml-p15824603p17324602")
parser.parse(sys.argv[1])

# Now, merge all these index files and then split it again. So we will have unique tokens (not repeated across multiple files)
# Step 1: Merge
MergeFiles()
# Step 2: Split for every 10000 tokens?
FinalSplit()





# All the Tags in the document:
# {'mediawiki': 1, 'siteinfo': 1, 'sitename': 1, 'dbname': 1, 'base': 1, 
# 'generator': 1, 'case': 1, 'namespaces': 1, 'namespace': 30, 'page': 476811, 
# 'title': 476811, 'ns': 476811, 'id': 1418993, 'revision': 476811, 
# 'parentid': 330666, 'timestamp': 476811, 'contributor': 476811, 
# 'username': 465371, 'minor': 196130, 'model': 476811, 'format': 476811, 
# 'text': 476811, 'sha1': 476811, 'comment': 448183, 'ip': 11437, 'redirect': 282745}

# Quarter Dump Stats:
# 1000 - 4m27.343s, 82mb