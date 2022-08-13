import xml.sax

# class PseudoGlobalVars:
#     def __init__(self):
#         self.index = -1
#         self.WikiEntries = []

#     def IncrementIndex(self):
#         self.index += 1

#     def NewWikiEntry(self):
#         self.IncrementIndex()
#         self.WikiEntries[self.index] = {"Title": "", "Text": ""}
    
#     def UpdateTitle(self, newTitle):
#         self.WikiEntries[self.index]["Title"] = newTitle

#     def UpdateText(self, NewText):
#         self.WikiEntries[self.index]["Text"] = NewText

class WikiHandler( xml.sax.ContentHandler):
    Storage = {"Index": -1, "WikiEntry": []}

    # @staticmethod
    # def IncrementIndex():
    #     Storage

    def IncrementIndex():
        WikiHandler.Storage["Index"] += 1
    
    def NewWikiEntry():
        WikiHandler.IncrementIndex()
        WikiHandler.Storage["WikiEntry"][WikiHandler.Storage["Index"]] = {"Title": "", "Text": ""}

    def UpdateTitle(newTitle):
        WikiHandler.Storage["WikiEntry"][WikiHandler.Storage["Index"]]["Title"] = newTitle

    def UpdateText(NewText):
        WikiHandler.Storage["WikiEntry"][WikiHandler.Storage["Index"]]["Text"] = NewText


    # Gets called when we start reading a tag
    def startElement(self, name):
        self.Tag = name
        if self.Tag == "page":
            # GlobalVars["index"] += 1
            WikiHandler.NewWikiEntry()

    # Characters is called when we are in the contents part ig?
    def characters(self, content):
        if self.Tag == 'title':
            # GlobalVars["WikiEntries"][GlobalVars["index"]] = {"Title" : content}
            WikiHandler.UpdateTitle(content)
        elif self.Tag == "text":
            # GlobalVars["WikiEntries"][GlobalVars["index"]]["Text"] = content
            WikiHandler.UpdateText(content)

    # End element get called when we are done reading the contents of the tag
    def endElement(self):
        self.Tags = ""

parser = xml.sax.make_parser()
parser.setContentHandler(WikiHandler())
parser.parse("enwiki-20220720-pages-articles-multistream15.xml-p15824603p17324602")        

# print(GlobalVars["WikiEntries"][1])
print(WikiHandler.Storage["WikiEntry"][1])

# All the Tags in the document:
# {'mediawiki': 1, 'siteinfo': 1, 'sitename': 1, 'dbname': 1, 'base': 1, 
# 'generator': 1, 'case': 1, 'namespaces': 1, 'namespace': 30, 'page': 476811, 
# 'title': 476811, 'ns': 476811, 'id': 1418993, 'revision': 476811, 
# 'parentid': 330666, 'timestamp': 476811, 'contributor': 476811, 
# 'username': 465371, 'minor': 196130, 'model': 476811, 'format': 476811, 
# 'text': 476811, 'sha1': 476811, 'comment': 448183, 'ip': 11437, 'redirect': 282745}