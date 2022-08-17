# After reading each page from the dump, we are going to process it and store it then and there, instead of getting all the files and then processing.

import xml.sax
# Regex
import re

Storage = {"WikiEntries": []}

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
            self.ResetData()

    def ProcessData(self):
        # Clean Text and extract components

        # Remove newline
        self.Text = re.sub("\n"," ",self.Text)

        # Casefolding: Removing uppercase
        self.Title = self.Title.lower()
        self.Text = self.Text.lower()

        print("******************")
        print("Body ",self.count," before Extracting Infobox")
        print(self.Text)
        print("******************")
        print()
        
        # Get Infobox
        self.GetInfobox()
        
        print("InfoBox: ")
        print(self.InfoBox)
        print()
        print("#################")
        # print("Body ",self.count," AFTER Extracting Infobox")
        # print(self.Text)
        # print("#################")
        # print()

        # Get References
        self.GetReferences()
        
        # Get Body
        # Get Category
        # Get Links

        # Tokenise
        # Stemming
        # Remove Stop words


    def GetInfobox(self):
        # Getting the Infobox data
        self.InfoBox = ' '.join(re.findall("(?<={{infobox)(.*?)(?=}})",self.Text))
        # Removing Infobox data from the text.
        self.Text = re.sub("({{infobox)(.*?)(}})"," ",self.Text)
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
        
    def GetCategories(self):
        self.Category = ' '.join(re.findall("(?<=\[\[category:)(.*?)(?=\]\])",self.References))
        # Removing Categories from References
        self.References = re.sub("(\[\[category:)(.*?)(\]\])", " ", self.References)
        print("(((((((((((((())))))))))")
        print("Categories: ")
        print(self.Category)
        print()

    def endDocument(self):
        print("Document Ended!!!")
        # return self.Storage


parser = xml.sax.make_parser()
parser.setContentHandler(WikiHandler())
parser.parse("enwiki-20220720-pages-articles-multistream15.xml-p15824603p17324602")
print(Storage["WikiEntries"][1])
print()
print(Storage["WikiEntries"][2])
print()
print(Storage["WikiEntries"][3])

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