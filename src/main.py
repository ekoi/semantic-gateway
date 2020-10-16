import io, urllib3, json

from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, RedirectResponse, StreamingResponse
from starlette.staticfiles import StaticFiles

from src.model import Vocabularies, WriteXML, ReadTsvFromUrl, CreateDVSettingJson

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
def fields_generator_get(request: Request):
    readTsvFromUrl = ReadTsvFromUrl(request, http)
    dv_setting_json = readTsvFromUrl.get_dv_setting_json()

    vocabularies = Vocabularies(conf_file_path)

    return templates.TemplateResponse('dv-cvm-setting-generator.html', context={'request': request, 'dv_setting_json' : dv_setting_json, 'ontologies': vocabularies.get_ontologies()})

@app.post("/dv/setting/edit")
async def push_dv_setting_post(request: Request):
    print('push')
    form_data = await request.form()
    return form_data

@app.post("/dv/setting/download")
async def download_dv_setting_post(request: Request):
    readTsvFromUrl = ReadTsvFromUrl(request, http)
    dv_setting_json = readTsvFromUrl.get_dv_setting_json()
    form_data = await request.form()
    createDVSettingJson = CreateDVSettingJson(form_data, dv_setting_json)
    createDVSettingJson.save_dv_json()
    return FileResponse('dv-setting.json', media_type='application/octet-stream', filename='dv-setting.json')
