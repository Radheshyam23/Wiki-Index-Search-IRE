import xml.sax

Storage = {"WikiEntries": []}

class WikiHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        # self.count = 0

    def startElement(self, name, attrs):
        self.Tag = name

        # if self.count >= 6:
        #     return

    # This gives us an array in which each entry is a ["Title","Content"].
    def characters(self, content):
        if self.Tag == "title":
            # # Just for testing
            # if self.count >= 6:
            #     return
            # self.count += 1
            Storage["WikiEntries"].append([content])

        elif self.Tag == "text":
            if len(Storage["WikiEntries"][-1]) == 1:
                Storage["WikiEntries"][-1].append(content)

            else:
                Storage["WikiEntries"][-1][1] += content

    def endElement(self, name):
        # if self.count >= 6:
        #     return
        self.Tag = ""
        # print("Element Ended")
    
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