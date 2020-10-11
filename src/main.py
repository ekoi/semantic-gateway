from fastapi import FastAPI, Request, Form, Response
import os



app = FastAPI()

@app.get('/')
def info():
    return {"name":"semantic gateway", "version":"1.0"}

@app.get('/configuration/{name}')
def get_configuration_data(name):
    print(name)
    try:
        content = open('data/' + name + '.xml', 'r')
        return Response(content=content.read(), media_type="application/xml")
    except:
        return "NOT FOUND"

@app.get('/configuration-list')
def get_configuration_list():
    arr = os.listdir('./data')
    return {"configurations": arr}