from fastapi import FastAPI, Form, Request, Response, HTTPException, Cookie, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()
templates = Jinja2Templates(directory=".")

@app.get("/{site}.html")
def loadSite(request: Request, site: str) :
    return templates.TemplateResponse(f"/{site}.html", {"request": request})

@app.get("/api/index")
def index(request : Request, password : str, id : str, pw : str) :
    if password == "zeropointerlab" : 
        os.system(f"adduser {id} -d /home/{id}; usermod -s /bin/bash {id}")
        os.system(f"echo '{id}:{pw}' | chpasswd")
        return templates.TemplateResponse(f"/info.html", {"request": request, "id" : id, "pw" : pw})
    else :
        return RedirectResponse("/index.html")