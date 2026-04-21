# main.py


from database import get_db
from fastapi import Depends, FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

# fastapi 객체 생성
app = FastAPI()
# jinja2 템플릿 객체 생성 (templates 파일들이 어디에 있는지 알려야 한다.)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "fortuneToday":"동쪽으로 가면 귀인을 만나요"
        }
    )

# get 방식 /post 요청 처리
@app.get("/post", response_class=HTMLResponse)
def getPosts(request: Request, db:Session = Depends(get_db)):
    # DB 에서 글목록을 가져오기 위한 sql 문 준비
    query = text("""
        SELECT num, writer, title, content, created_at
        FROM post
        ORDER BY num DESC
    """)
   
    # 글 목록 얻어와서
    result = db.execute(query)
    posts = result.fetchall()
    # 응답하기
    return templates.TemplateResponse(
        request=request,
        name="/post/list.html",
        context={
            "posts":posts
        }
    )

@app.get("/post/new", response_class=HTMLResponse)
def postNew(request: Request):
    return templates.TemplateResponse(request=request, name="post/new-form.html")

@app.post("/post/new")
def postNew(request: Request, writer: str = Form(...), title: str = Form(...), content: str = Form(...), 
            db: Session = Depends(get_db)):
    #DB에 저장할 sql 문 준비
    query = text("""
        INSERT INTO post
        (writer, title, content)
        VALUES(:writer, :title, :content)
    """)
    db.execute(query, {"writer":writer, "title":title, "content":content})
    db.commit()

    # 특정 경로로 요청을 다시 하도록 리이다이렉트 응답준다.
    # return RedirectResponse("/post", status_code=302)
    return templates.TemplateResponse(
        request=request, 
        name="post/alert.html",
        context={
            "msg": "글 정보를 추가 했습니다!",
            "url": "/post"
        })

@app.get("/post/delete/{num}")
def postDelete(num: int, db: Session = Depends(get_db)):
    # DB에서 삭제할 sql 문 준비
    query = text("""
        DELETE FROM post
        WHERE num = :num
    """)
    db.execute(query, {"num": num})
    db.commit()

    # 삭제 후 목록(/post)으로 리다이렉트
    return RedirectResponse("/post", status_code=302)

@app.get("/post/edit/{num}", response_class=HTMLResponse)
def editForm(num: int, request: Request, db: Session = Depends(get_db)):
    # 수정을 위해 기존 데이터를 가져오는 SQL
    query = text("""
        SELECT num, writer, title, content, created_at
        FROM post
        WHERE num = :num
    """)
    row = db.execute(query, {"num": num}).fetchone()
    
    #pk 를 이용해서 select하는거여서 row는 1개다.따라서 .fetchone()함수 요청
    return templates.TemplateResponse(
        request=request, 
        name="post/edit.html", 
        context={
            "post": row
        }
    )

@app.post("/post/edit/{num}")
def edit(request:Request, num: int, title: str = Form(...), content: str = Form(...), 
               db: Session = Depends(get_db)):
    # DB에 수정할 sql 문 준비
    query = text("""
        UPDATE post
        SET title = :title, content = :content
        WHERE num = :num
    """)
    db.execute(query, {"num": num,"title": title, "content": content})
    db.commit()

    return templates.TemplateResponse(
        request=request, 
        name="post/alert.html",
        context={
            "msg":"글 정보를 수정 했습니다!",
            "url":"/post"
        }
    )