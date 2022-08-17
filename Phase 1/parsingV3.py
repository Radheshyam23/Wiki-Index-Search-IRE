import xml.sax
from os.path import exists

Storage = {"WikiEntries": []}

# Going to print everything so that we can redirect into a file.
class WikiHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
      
    def startElement(self, name, attrs):
        self.Tag = name
        if self.Tag == "title":
            print("Title: ",self.Tag, file=WikiTitleText_FilePtr)

    def characters(self, content):
        if self.Tag == "text":
            print(content, file=WikiTitleText_FilePtr)

    def endElement(self, name):
        print("EndOfPage!!!", file=WikiTitleText_FilePtr)

    def endDocument(self):
        print("EndOfDoc!!!", file=WikiTitleText_FilePtr)

WikiTitleText_File = "WikiTitleTextDump.txt"
if not exists(WikiTitleText_File):
    WikiTitleText_FilePtr = open(WikiTitleText_File,'w')
    parser = xml.sax.make_parser()
    parser.setContentHandler(WikiHandler())
    parser.parse("enwiki-20220720-pages-articles-multistream15.xml-p15824603p17324602")

# print(Storage["WikiEntries"][1])
# print()
# print(Storage["WikiEntries"][2])
# print()
# print(Storage["WikiEntries"][3])

# {'Title': 'Wikipedia:WikiProject Spam/LinkReports/izteremka.com', 'Text': '>'}
# {'Title': 'Pushmataha Area Council', 'Text': '[[Category:1925 establishments in Mississippi]]'}
# {'Title': 'Wikipedia:Peer review/McMansion', 'Text': '#REDIRECT [[Wikipedia:Peer review/McMansion/archive1]]'}


26th OSN QUIZ