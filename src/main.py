from fastapi import FastAPI, Request, Form, Response

app = FastAPI()

@app.get('/')
def read_form():
    return {"name":"semantic gateway", "version":"1.0"}

@app.get('/configuration/{name}')
def get_legacy_data(name):
    print(name)
    try:
        content = open('data/' + name + '.xml', 'r')
        return Response(content=content.read(), media_type="application/xml")
    except:
        return "NOT FOUND"