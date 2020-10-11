import xml.etree.ElementTree as ET
class Vocabularies:
    "This is a Vocabularies class"
    def __init__(self, name):
        self.root = ET.parse('./data/' + name + '.xml').getroot()

    def get_ontologies(self):
        ontologies = []
        for atype in self.root.findall('.//ontology'):
            ontology = Ontology(atype)
            ontologies.append(ontology)

        return ontologies

class Ontology:
    def __init__(self, name):
        self.name = name.attrib['name']

    def get_name(self):
        return self.name
