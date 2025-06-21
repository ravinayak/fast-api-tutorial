from fastapi import FastAPI, Depends, Response, status, HTTPException
from . import models, schemas
from sqlalchemy.orm import Session
from .database import SessionLocal, engine

app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
  db = SessionLocal()
  try:
      yield db
  finally:
      db.close()

@app.post('/create')
def create(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title = request.title, body = request.message)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get('/blogs', status_code = status.HTTP_200_OK)
def blogs(response: Response, db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    if not blogs:
        response.status_code = status.HTTP_404_NOT_FOUND
        return { 'data': blogs }
    return blogs

@app.get('/blog/{id}')
def show(id: int, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'No blog with {id} found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return { 'data': [] }
    return { 'data': [blog] }