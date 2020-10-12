from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from src.model import Vocabularies, WriteXML

app = FastAPI()
templates = Jinja2Templates(directory='templates/')
app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/')
def info():
    return {"name":"semantic gateway", "version":"1.0"}

@app.get('/configuration/xml')
def get_configuration_xml():
    try:
        content = open('./data/gateway.xml', 'r')
        return Response(content=content.read(), media_type="application/xml")
    except:
        return "NOT FOUND"

@app.get('/configuration/view')
def get_configuration_html_view(request: Request):
    vocabularies = Vocabularies('gateway.xml')
    return templates.TemplateResponse('configuration-view.html', context={'request': request, 'ontologies': vocabularies.get_ontologies()})

@app.get('/configuration/edit')
def get_configuration_html_view(request: Request):
    vocabularies = Vocabularies('gateway.xml')
    return templates.TemplateResponse('configuration-edit.html', context={'request': request, 'ontologies': vocabularies.get_ontologies()})

@app.post("/configuration/edit")
async def modify_configuration_post(request: Request):
    form_data = await request.form()
    writeXML = WriteXML(form_data.items());
    writeXML.save()
    try:
        content = open('./data/gateway-conf.xml', 'r')
        return Response(content=content.read(), media_type="application/xml")
    except:
        return "NOT FOUND"
    # return form_data

@app.get('/configuration/download')
def download():
    return FileResponse('./data/gateway-conf.xml', media_type='application/octet-stream', filename='gateway-conf.xml')