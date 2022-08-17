# After reading each page from the dump, we are going to process it and store it then and there, instead of getting all the files and then processing.

import sys
import xml.sax
# Regex
import re
from nltk.corpus import stopwords
# import nltk
# nltk.download('stopwords')
from collections import defaultdict
from nltk.stem import SnowballStemmer
import os

Storage = {"PageNum": 0, "IndexFileNum": 0, "PostingLists": defaultdict(list), "offset": 0, "dictID": {}}

StopWordsExtension = ["jpg"]

class BagOfWords():

    def __init__(self):
        self.StopWords = set(stopwords.words("english"))
        self.StopWordsDict = defaultdict(int)
        for stop in self.StopWords:
            self.StopWordsDict[stop] = 1
        self.SnowStem = SnowballStemmer('english')

    def Tokenize(self,unrefinedStr):
        unrefinedStr = re.sub(r'http[^\ ]*\ ', r' ', unrefinedStr) # removing urls
        # unrefinedStr = re.sub(r'\S+\.com\S+',' ', unrefinedStr) # removing urls
        unrefinedStr = re.sub(r'\—|\'|\`|\"|\||\.|\*|\[|\{|\}|\(|\)|\]|\;|\:|\,|\=|\-|\+|\_|\!|\?|\/|\>|\<|\&|\\|\#|\n', r' ', unrefinedStr) # removing special characters
        unrefinedStr = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', unrefinedStr) # removing html entities
        return unrefinedStr.split()

    def StopANDStem(self, Bag):
        Bag = [self.SnowStem.stem(word) for word in Bag if self.StopWordsDict[word] != 1]
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
            print("Page: ",Storage["PageNum"])
            self.ResetData()

    def ProcessData(self):
        # Clean Text and extract components

        # Remove newline
        self.Text = re.sub("\n"," ",self.Text)

        # Casefolding: Removing uppercase
        self.Title = self.Title.lower()
        self.Text = self.Text.lower()

        # Get Infobox
        self.GetInfobox()
        
        # print("IIIIIIIIII")
        # print("InfoBox: ")
        # print(self.InfoBox)
        # print("IIIIIIIII")
        # print()
        
        # Get References. This also gets Categories and External Links
        self.GetReferences()

        # self.Body = re.sub('[|=\[\]\{\}\(\)\'\"]',' ',self.Body)

        # print("BBBBBBBBB")
        # print("Body ",self.count," After Extracting Categories")
        # print(self.Body)
        # print("BBBBBBBBB")
        # print()

        # print("Title")
        # print(self.Title)
        # print()

        # print("Infobox")
        # print(self.InfoBox)
        # print()

        # print("Body")
        # print(self.Body)
        # print()

        # print("Categories")
        # print(self.Category)
        # print()

        # print("References")
        # print(self.References)
        # print()

        # print("External Links")
        # print(self.Links)
        # print()

        # print("##################################")

        # Bag of Words
        BOW = BagOfWords()
        # Tokenise
        self.Title = BOW.Tokenize(self.Title)
        self.Body = BOW.Tokenize(self.Body)
        self.InfoBox = BOW.Tokenize(self.InfoBox)
        self.Category = BOW.Tokenize(self.Category)
        self.References = BOW.Tokenize(self.References)
        self.Links = BOW.Tokenize(self.Links)

        # print("Title")
        # print(self.Title)
        # print()

        # print("Infobox")
        # print(self.InfoBox)
        # print()

        # print("Body")
        # print(self.Body)
        # print()

        # print("Categories")
        # print(self.Category)
        # print()

        # print("References")
        # print(self.References)
        # print()

        # print("External Links")
        # print(self.Links)
        # print()

        # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        # Removing Stop words and Stemming
        self.Title = BOW.StopANDStem(self.Title)
        self.Body = BOW.StopANDStem(self.Body)
        self.InfoBox = BOW.StopANDStem(self.InfoBox)
        self.Category = BOW.StopANDStem(self.Category)
        self.References = BOW.StopANDStem(self.References)
        self.Links = BOW.StopANDStem(self.Links)
        
        # print("Title")
        # print(self.Title)
        # print()

        # print("Infobox")
        # print(self.InfoBox)
        # print()

        # print("Body")
        # print(self.Body)
        # print()

        # print("Categories")
        # print(self.Category)
        # print()

        # print("References")
        # print(self.References)
        # print()

        # print("External Links")
        # print(self.Links)
        # print()

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

        # print("RRRRRRRRRR")
        # print(self.References)
        # print("RRRRRRRRRRR")
        # print()

        
    def GetCategories(self):
        self.Category = ' '.join(re.findall("(?<=\[\[category:)(.*?)(?=\]\])",self.References))
        # Removing Categories from References
        self.References = re.sub("(\[\[category:)(.*?)(\]\])", " ", self.References)
        # print("CCCCCCCCCCCCc")
        # print("Categories: ")
        # print(self.Category)
        # print("CCCCCCCCCCCCc")
        # print()

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

            # print("EEEEEEEEE")
            # print(self.Links)
            # print("EEEEEEEEEe")
            # print()
    
    def Indexing(self):
        PageIndexer = Indexing(self.Title, self.InfoBox, self.Body, self.Category, self.References, self.Links)
        PageIndexer.CreateIndex()


    def endDocument(self):
        print("Document Ended!!!")
        # return self.Storage


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
        if Storage["PageNum"]%25000 == 0:
            writeIntoFile()
            Storage["PostingLists"] = defaultdict(list)
            Storage["dictID"] = {}
            Storage["IndexFileNum"] += 1



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

parser = xml.sax.make_parser()
parser.setContentHandler(WikiHandler())
# parser.parse("/home/radheshyam/Desktop/Year3_1/IREL/IREL-MiniProject/Phase 1/enwiki-20220720-pages-articles-multistream15.xml-p15824603p17324602")
parser.parse(sys.argv[1])


# print(Storage["WikiEntries"][1])
# print()
# print(Storage["WikiEntries"][2])
# print()
# print(Storage["WikiEntries"][3])

# {'Title': 'Wikipedia:WikiProject Spam/LinkReports/izteremka.com', 'Text': '>'}
# {'Title': 'Pushmataha Area Council', 'Text': '[[Category:1925 establishments in Mississippi]]'}
# {'Title': 'Wikipedia:Peer review/McMansion', 'Text': '#REDIRECT [[Wikipedia:Peer review/McMansion/archive1]]'}

# All the Tags in the document:
# {'mediawiki': 1, 'siteinfo': 1, 'sitename': 1, 'dbname': 1, 'base': 1, 
# 'generator': 1, 'case': 1, 'namespaces': 1, 'namespace': 30, 'page': 476811, 
# 'title': 476811, 'ns': 476811, 'id': 1418993, 'revision': 476811, 
# 'parentid': 330666, 'timestamp': 476811, 'contributor': 476811, 
# 'username': 465371, 'minor': 196130, 'model': 476811, 'format': 476811, 
# 'text': 476811, 'sha1': 476811, 'comment': 448183, 'ip': 11437, 'redirect': 282745}