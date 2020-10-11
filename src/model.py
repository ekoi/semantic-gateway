import xml.etree.ElementTree as ET
class Vocabularies:
    "This is a Vocabularies class"
    def __init__(self, name):
        self.root = ET.parse('./data/' + name).getroot()

    def get_ontologies(self):
        ontologies = []
        for atype in self.root.findall('.//ontology'):
            ontology = Ontology(atype)
            ontologies.append(ontology)

        return ontologies

class Ontology:
    def __init__(self, element):
        self.element  = element

    def get_name(self):
        return self.element.attrib['name']

    def get_type(self):
        return self.element.find('type').text

    def get_url(self):
        base_url = self.element.find('api').text
        uri =  self.element.find('parameters/uri')
        if uri is not None:
            print(uri.text)
            return base_url +  '/' + uri.text
        else:
            return base_url
