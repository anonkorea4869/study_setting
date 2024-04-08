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

    with open(f'/home/{id}/.ssh/smart', 'r') as file:
        public_key = file.read()
    public_key = str(public_key)
    public_key = public_key[public_key.find('----') : public_key.find('-----END OPENSSH PRIVATE KEY-----') + len('-----END OPENSSH PRIVATE KEY-----')]

    return public_key

def savePassword(id, pw) :
    os.system(f"touch /home/{id}/.ssh/password")
    os.system(f"echo '{pw}' > /home/{id}/.ssh/password")
    os.system(f"chown {id}:{id} /home/{id}/.ssh/password")

def findPassword(id) :
    with open(f'/home/{id}/.ssh/password', 'r') as file:
        password = file.read().replace("\n", "")
        return password

def findPublicKey(id) :
    with open(f'/home/{id}/.ssh/smart', 'r') as file:
        public_key = file.read()
        return public_key

@app.get("/{site}.html")
def loadSite(request: Request, site: str) :
    return templates.TemplateResponse(f"/{site}.html", {"request": request})

@app.get("/api/index")
def index(request : Request, password : str, id : str, pw : str) :
    if password == "zeropointerlab" :
        # 패스워드 규칙 조회
        if len(pw) < 8 or id in pw :
            return RedirectResponse("/index.html")

        try: # 계정 이미 존재하는지
            subprocess.run(["id", id], check=True, capture_output=True)
            find_pw = findPassword(id)

            if find_pw == pw : # 사용자 입력 비밀번호와 실제 비밀번호가 같으면
                public_key = findPublicKey(id)
                return templates.TemplateResponse(f"/info.html", {"request": request, "id" : id, "pw" : pw, "Pk" : public_key})
            else : 
                return RedirectResponse("/index.html")

        except subprocess.CalledProcessError:
            pass

        createUser(id, pw)
        public_key = createKey(id)
        savePassword(id, pw)

        return templates.TemplateResponse(f"/info.html", {"request": request, "id" : id, "pw" : pw, "Pk" : public_key})
    else :
        return RedirectResponse("/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port = 80)