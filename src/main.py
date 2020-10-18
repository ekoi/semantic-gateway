import os
from typing import List
import urllib.parse
import urllib3, json, validators, shutil

from fastapi import FastAPI, Request, Response, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, RedirectResponse, StreamingResponse
from starlette.staticfiles import StaticFiles

from src.model import Vocabularies, WriteXML, ReadTsvFromUrl, CreateDVSettingJson, ReadTsvFromLocalFile
import time

current_milli_time = lambda: int(round(time.time() * 1000))

app = FastAPI()
templates = Jinja2Templates(directory='templates/')
app.mount('/static', StaticFiles(directory='static'), name='static')

conf_file_path = './data/gateway.xml'
http = urllib3.PoolManager()

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
def fields_generator_get(request: Request, tsv_url:str='', tsv_fn:str=''):

    dv_setting_json=[]
    vocabularies = Vocabularies(conf_file_path)
    if validators.url(tsv_url):
        if str(tsv_url).endswith('.tsv'):
            readTsvFromUrl = ReadTsvFromUrl(request, http, tsv_url)
            dv_setting_json = readTsvFromUrl.get_dv_setting_json()
        else:
            return "Invalid tsv file"
    else:
        if tsv_fn != '' and tsv_url == '':
            try:
                content = open('./data/' + tsv_fn + '.tsv', 'r')
                readTsvFromContent = ReadTsvFromLocalFile(content)
                dv_setting_json = readTsvFromContent.get_dv_setting_json()
            except:
                return "Invalid tsv file"

    return templates.TemplateResponse('dv-cvm-setting-generator.html', context={'request': request, 'dv_setting_json' : dv_setting_json
                                        , 'ontologies': vocabularies.get_ontologies(), 'tsv_url':tsv_url, 'tsv_fn':tsv_fn})

@app.post("/dv/setting/edit")
async def push_dv_setting_post(request: Request, tsv_url:str='', tsv_fn:str=''):
    form_data = await request.form()
    gateway_url = form_data['gateway_url']
    if not validators.url(gateway_url):
        return "Invalid Gateway URL"
    else:
        if tsv_fn != '':
            content = open('./data/' + tsv_fn + '.tsv', 'r')
            readTsvFromContent = ReadTsvFromLocalFile(content)
            dv_setting_json = readTsvFromContent.get_dv_setting_json()
        else:
            readTsvFromUrl = ReadTsvFromUrl(request, http, tsv_url, form_data['gateway_url'])
            dv_setting_json = readTsvFromUrl.get_dv_setting_json()

        createDVSettingJson = CreateDVSettingJson(form_data, dv_setting_json)
        encoded_data = json.dumps(createDVSettingJson.get_dv_json()).encode('utf-8')
        dv_api_url = createDVSettingJson.get_dv_url() + '/api/admin/settings/:CVMConf?unblock-key=' + createDVSettingJson.get_api_token()

        resp = http.request(
            'PUT',
            dv_api_url,
            body=encoded_data,
            headers={'Content-Type': 'application/json'})

        if resp.status == 200:
            result = json.loads(resp.data.decode('utf-8'))
            if result.get('status') == 'OK':
                return result.get('data')
            elif result.get('status') == 'error':
                return result.get('message')
            else:
                return 'Other errors: ' + str(result)
        else:
            try:
                result = json.loads(resp.data.decode('utf-8'))
                return result.get('data')
            except:
                return str(resp.status)

@app.post("/dv/setting/download")
async def download_dv_setting_post(request: Request, tsv_url:str='', tsv_fn:str=''):
    form_data = await request.form()
    gateway_url = form_data['gateway_url']
    if not validators.url(gateway_url):
        return "Invalid Gateway URL"
    else:
        if tsv_fn != '':
            try:
                content = open('./data/' + tsv_fn + '.tsv', 'r')
                readTsvFromContent = ReadTsvFromLocalFile(content)
                dv_setting_json = readTsvFromContent.get_dv_setting_json()
            except:
                return "Invalid tsv file"

        else:
            readTsvFromUrl = ReadTsvFromUrl(request, http, tsv_url, gateway_url)
            dv_setting_json = readTsvFromUrl.get_dv_setting_json()
        createDVSettingJson = CreateDVSettingJson(form_data, dv_setting_json)
        x = createDVSettingJson.get_dv_json()
        if len(x) == 0:
            return "No selected vocabulary"
        createDVSettingJson.save_dv_json()

    return FileResponse('dv-setting.json', media_type='application/octet-stream', filename='dv-setting.json')

@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    UPLOAD_DIRECTORY = "./data"
    contents = await file.read()
    fname = str(current_milli_time())
    with open(os.path.join(UPLOAD_DIRECTORY, fname + '.tsv'), "wb") as fp:
            fp.write(contents)

    return RedirectResponse(url='/dv/setting/edit?tsv_url=&tsv_fn=' + fname, status_code=302)