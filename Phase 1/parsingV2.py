import xml.sax

Storage = {"WikiEntries": []}

class WikiHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        # self.Storage = []

    def startElement(self, name, attrs):
        self.Tag = name
    
    def characters(self, content):
        if self.Tag == "title":
            # self.Title = content
            # self.Storage.append([self.Title])
            Storage["WikiEntries"].append([content])

        elif self.Tag == "text":
            if len(Storage["WikiEntries"][-1]) == 1:
                # self.Storage[-1].append(content)
                Storage["WikiEntries"][-1].append(content)

            else:
                # self.Storage[-1][1] += content
                Storage["WikiEntries"][-1][1] += content


    # def characters(self, content):
    #     if self.Tag in ['mediawiki','siteinfo', 'sitename', 'dbname', 'base','generator', 'case', 'namespaces', 'namespace']:
    #         pass
    #     elif self.Tag == "page":
    #         Storage["WikiEntry"].append({})
    #     else:
    #         Storage["WikiEntry"][-1][self.Tag] = content



    # def characters(self, content):
    #     print(self.Tag,":")
    #     print(content)
    #     print("----------")
    #     print()
        


    def endElement(self, name):
        self.Tag = ""
        # print("Element Ended")
    
    def endDocument(self):
        print("Document Ended!!!")
        # return self.Storage


parser = xml.sax.make_parser()
parser.setContentHandler(WikiHandler())
parser.parse("enwiki-20220720-pages-articles-multistream15.xml-p15824603p17324602")
print(Storage["WikiEntries"][1])
print(Storage["WikiEntries"][2])
print(Storage["WikiEntries"][3])

# {'Title': 'Wikipedia:WikiProject Spam/LinkReports/izteremka.com', 'Text': '>'}
# {'Title': 'Pushmataha Area Council', 'Text': '[[Category:1925 establishments in Mississippi]]'}
# {'Title': 'Wikipedia:Peer review/McMansion', 'Text': '#REDIRECT [[Wikipedia:Peer review/McMansion/archive1]]'}