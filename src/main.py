import io
import urllib3
import json

from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, RedirectResponse, StreamingResponse
from starlette.staticfiles import StaticFiles

from src.model import Vocabularies, WriteXML

app = FastAPI()
templates = Jinja2Templates(directory='templates/')
app.mount('/static', StaticFiles(directory='static'), name='static')

conf_file_path = './data/gateway.xml'
http = urllib3.PoolManager()
dv_setting_json = []

@app.get('/')
def info():
    return {"name":"semantic gateway", "version":"1.0"}

@app.get('/configuration/xml')
def get_configuration_xml():
    try:
        content = open(conf_file_path, 'r')
        return Response(content=content.read(), media_type="application/xml")
    except:
        return "NOT FOUND"

@app.get('/configuration/view')
def get_configuration_html_view(request: Request):
    vocabularies = Vocabularies(conf_file_path)
    return templates.TemplateResponse('configuration-view.html', context={'request': request, 'ontologies': vocabularies.get_ontologies()})

@app.get('/configuration/edit')
def get_configuration_html_view(request: Request):
    vocabularies = Vocabularies(conf_file_path)
    return templates.TemplateResponse('configuration-edit.html', context={'request': request, 'ontologies': vocabularies.get_ontologies()})

@app.post("/configuration/edit")
async def modify_configuration_post(request: Request):
    form_data = await request.form()
    writeXML = WriteXML(form_data.items());
    writeXML.save(conf_file_path)
    return RedirectResponse(url='/configuration/view', status_code=302)

@app.get('/configuration/download')
def download():
    return FileResponse(conf_file_path, media_type='application/octet-stream', filename='gateway-conf.xml')

@app.get('/dv/setting/edit')
def get_fields_composer(request: Request):
    dv_setting_json = []
    print("---------------------------------------")

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
                dv_setting_json.append(dv_setting_el)

            else:
                print('error')

        if json_process == 'finish':
            json_process = ''

    vocabularies = Vocabularies(conf_file_path)

    return templates.TemplateResponse('dv-cvm-setting-generator.html', context={'request': request, 'dv_setting_json' : dv_setting_json, 'ontologies': vocabularies.get_ontologies()})

@app.post("/dv/setting/edit")
async def push_dv_setting_post(request: Request):
    print('push')
    form_data = await request.form()
    return form_data

@app.post("/dv/setting/download")
async def download_dv_setting_post(request: Request):
    for dv in dv_setting_json:
        print(dv['vocab-name'])

    form_data = await request.form()
    form_inputs = form_data.items()
    for dv in dv_setting_json:
        dv['vocabs']=[]
    dv_json=[]
    for key, value in form_inputs:
        if key not in ['dv_url','dv_api_token']:
            for dv in dv_setting_json:
                if str(key).startswith(dv['vocab-name']):
                    dv['vocabs'].append(str(key).split('|')[1])
                    dv_json.append(dv)

    with open('dv-setting.json', 'w') as json_file:
        json.dump(dv_json, json_file)
    return FileResponse('dv-setting.json', media_type='application/octet-stream', filename='dv-setting.json')
