from fastapi import FastAPI, Form, Request, Response, HTTPException, Cookie, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import subprocess

app = FastAPI()
templates = Jinja2Templates(directory=".")

def createUser(id, pw) :
    os.system(f"useradd -m {id}")
    os.system(f"usermod -s /bin/bash {id}")
    os.system(f"echo '{id}:{pw}' | chpasswd")

def createKey(id) :
    os.system(f"mkdir -p /home/{id}/.ssh/")
    os.system(f"chmod 700 /home/{id}/.ssh/")
    os.system(f"ssh-keygen -t rsa -b 2048 -f /home/{id}/.ssh/smart -N ''")
    os.system(f"cp /home/{id}/.ssh/smart.pub /home/{id}/.ssh/authorized_keys")
    os.system(f"chmod 600 /home/{id}/.ssh/authorized_keys")
    os.system(f"chown -R {id}:{id} /home/{id}/.ssh/")

    public_key = subprocess.run(["cat", f'/home/{id}/.ssh/smart'], capture_output=True, text=True)
    public_key = str(public_key)
    public_key = public_key[public_key.find('----') : public_key.find('-----END OPENSSH PRIVATE KEY-----') + len('-----END OPENSSH PRIVATE KEY-----')]

    return public_key

@app.get("/{site}.html")
def loadSite(request: Request, site: str) :
    return templates.TemplateResponse(f"/{site}.html", {"request": request})

@app.get("/api/index")
def index(request : Request, password : str, id : str, pw : str) :
    if password == "zeropointerlab" :
        패스워드 규칙 조회
        if len(pw) < 8 or id in pw :
            return RedirectResponse("/index.html")

        try: # 계정 이미 존재하는지
            subprocess.run(["id", id], check=True, capture_output=True)
            return RedirectResponse("/index.html")
        except subprocess.CalledProcessError:
            pass

        createUser(id, pw)
        public_key = createKey(id)

        return templates.TemplateResponse(f"/info.html", {"request": request, "id" : id, "pw" : pw, "Pk" : public_key})
    else :
        return RedirectResponse("/index.html")