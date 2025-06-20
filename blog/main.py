from fastapi import FastAPI, Depends
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