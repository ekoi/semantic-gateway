from fastapi import FastAPI, Request, Form, Response
from fastapi.templating import Jinja2Templates
import os
import xml.etree.ElementTree

from src.model import Vocabularies

app = FastAPI()
templates = Jinja2Templates(directory='templates/')

@app.get('/')
def info():
    e = xml.etree.ElementTree.parse('./data/gateway.xml').getroot()
    for atype in e.findall('.//ontology'):
        print(atype.attrib['name'])
        # print("%s | %s" % (atype.find('type').text, atype.find('api').text))

    return {"name":"semantic gateway", "version":"1.0"}

@app.get('/configuration/{name}/xml')
def get_configuration_data(name):
    print(name)
    try:
        content = open('data/' + name + '.xml', 'r')
        return Response(content=content.read(), media_type="application/xml")
    except:
        return "NOT FOUND"

@app.get('/configuration/{name}')
def  form_post(request: Request, name):
    vocabularies = Vocabularies(name)
    return templates.TemplateResponse('configuration.html', context={'request': request, 'result': vocabularies.get_ontologies()})

@app.get('/configuration-list')
def get_configuration_list():
    arr = os.listdir('./data')
    return {"configurations": arr}

