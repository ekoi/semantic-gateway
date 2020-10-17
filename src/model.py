import xml.etree.ElementTree as ET
import io, urllib3, json

class Vocabularies:
    "This is a Vocabularies class"
    def __init__(self, path):
        self.root = ET.parse(path).getroot()

    def get_ontologies(self):
        ontologies = []
        for i, atype in enumerate(self.root.findall('.//ontology')):
            ontology = Ontology(i, atype)
            ontologies.append(ontology)

        return ontologies

class Ontology:
    def __init__(self, i, element):
        self.i = i
        self.element  = element
    def get_index(self):
        return self.i

    def get_name(self):
        return self.element.attrib['name']

    def get_type(self):
        return self.element.find('type').text

    def get_vocabulary(self):
        v = self.element.find('vocabulary')
        if v is not None:
            return self.element.find('vocabulary').text
        return ''

    def get_base_url(self):
        return self.element.find('api').text

    def get_uri(self):
        u = self.element.find('parameters/uri')
        if u is not None:
            return u.text
        return ''

    def get_url(self):
        return self.get_base_url() + '/' + self.get_uri()

    def get_vocab(self):
        u = self.element.find('parameters/vocab')
        if u is not None:
            return u.text
        return ''

    def get_query(self):
        u = self.element.find('parameters/query')
        if u is not None:
            return u.text
        return ''

    def get_lang(self):
        u = self.element.find('parameters/lang')
        if u is not None:
            return u.text
        return ''


class WriteXML:
    root = ET.Element('vocabularies');
    def __init__(self, form_inputs):
        #Remove all vocabularies children
        for child in self.root.findall('.//ontology'):
            self.root.remove(child)
        for key, value in form_inputs:
            if str(value).strip() != '':
                if str(key).startswith('inputName_'):
                    ontology = ET.SubElement(self.root, 'ontology')
                    ontology.set('name',str(value))
                if str(key).startswith('inputType_'):
                    type = ET.SubElement(ontology, 'type')
                    type.text = str(value)
                if str(key).startswith('inputVocabulary_'):
                    voc = ET.SubElement(ontology, 'vocabulary')
                    voc.text = str(value)
                if str(key).startswith('inputBaseUrl_'):
                    api = ET.SubElement(ontology, 'api')
                    api.text = str(value)
                    parameters = ET.SubElement(ontology, 'parameters')

                if str(key).startswith('inputUri_'):
                    uri = ET.SubElement(parameters, 'uri')
                    uri.text = str(value)

                if str(key).startswith('inputVocab_'):
                    vocab = ET.SubElement(parameters, 'vocab')
                    vocab.text = str(value)

                if str(key).startswith('inputQuery_'):
                    query = ET.SubElement(parameters, 'query')
                    query.text = str(value)

                if str(key).startswith('inputLang_'):
                    lang = ET.SubElement(parameters, 'lang')
                    lang.text = str(value)

        # create a new XML file with the results
    def save(self, path):
        mydata = ET.tostring(self.root, encoding='UTF8', method='xml')
        myfile = open(path, 'wb')
        myfile.seek(0)
        myfile.truncate()
        myfile.seek(0)
        myfile.write(mydata)
        myfile.close()

class ReadTsvFromUrl:
    dv_setting_json = []
    def __init__(self,request, http):
        self.dv_setting_json = []
        r = http.request('GET', "https://raw.githubusercontent.com/ekoi/speeltuin/master/resources/CMM_Custom_MetadataBlock.tsv")
        d = r.data.decode('utf-8')
        s = io.StringIO(d)
        template='{"vocab-name":"AKMI_KEY", "cvm-url":"' + str(request.base_url) +'", "language":"LANGUAGE", "vocabs":["VOC"],"vocab-codes": ["KV","KT","KU"]}';
        json_process = ''
        json_element = ''
        json_text = ''
        dv_setting_el = {}
        for line in s:
            abc = line.split('\t')
            if json_process == '' and abc[1].endswith('-cv'):
                json_element = template.replace('AKMI_KEY',abc[1])
                json_element = json_element.replace('VOC', abc[2])
                json_process='create'
            elif json_process  == 'create':
                if abc[1].endswith('-vocabulary'):
                    json_element = json_element.replace('KV', abc[1])
                elif abc[1].endswith('-term'):
                    json_element = json_element.replace('KT', abc[1])
                elif abc[1].endswith('-url'):
                    json_element = json_element.replace('KU', abc[1])
                    json_process="finish";
                    dv_setting_el = json.loads(json_element)
                    # print(dv_setting_el)
                    self.dv_setting_json.append(dv_setting_el)

                else:
                    print('error')

            if json_process == 'finish':
                json_process = ''

    def get_dv_setting_json(self):
        return self.dv_setting_json

class CreateDVSettingJson:
    dv_json = []
    dv_url : str = ''
    dv_api_token : str = ''
    def __init__(self, form_data, dv_setting_json):
        form_inputs = form_data.items()
        for dv in dv_setting_json:
            dv['vocabs']=[]
        self.dv_json=[]
        for key, value in form_inputs:
            if key not in ['dv_url','dv_api_token']:
                for dv in dv_setting_json:
                    if str(key).startswith(dv['vocab-name']):
                        dv['vocabs'].append(str(key).split('|')[1])
                        if not (any(tag['vocab-name'] == dv['vocab-name'] for tag in self.dv_json)):
                            self.dv_json.append(dv)
            else:
                if key == 'dv_api_token':
                    self.dv_api_token = value
                else:
                    self.dv_url = value
    def get_dv_url(self):
        return self.dv_url

    def get_api_token(self):
        return self.dv_api_token

    def save_dv_json(self):
        with open('dv-setting.json', 'w') as json_file:
            json_file.seek(0)
            json_file.truncate()
            json.dump(self.dv_json, json_file)
            json_file.close()

    def get_dv_json(self):
        return self.dv_json
