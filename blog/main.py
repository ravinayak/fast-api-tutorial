from fastapi import FastAPI, Depends, Response, status, HTTPException
from . import models, schemas
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from pprint import pprint

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
    pprint(request.model_dump())
    # Both the methods are acceptable
    # pprint improves print formatting for key/value pairs
    # request.model_dump = { title: 'title', message: 'message', published: 'published' }
    # **request.model_dump converts the hash/dict into keyword arguments for the method, calls the method with
    # **request.model_dump = { title = 'title', message = 'message', published = 'published' }	
    # modles.Blog(**request.model_dump()) = models.Blog(title='title', message='message', published='published')
    # print/pprint does not take arbitrary keyword arguments, hence pprint(**request.model_dump()) will fail [with print as well]
    # print(key1=value1, key2=value2) is INVALID
    # models.Blog(**request.model_dump()) is VALID
    # new_blog = models.Blog(title = request.title, message = request.message, published = request.published)
    new_blog = models.Blog(**request.model_dump())
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
def show(id: int, _response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'No blog with {id} found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return { 'data': [] }
    return { 'data': [blog] }

@app.put('/blog/{id}', status_code = status.HTTP_201_CREATED)
def update(id: int, request: schemas.Blog, response: Response, db: Session = Depends(get_db)):
	blog = db.query(models.Blog).filter(models.Blog.id == id)
	if not blog.first():
		response.status_code = status.HTTP_404_NOT_FOUND
		return { 'data': [] }
	# update expects a dictionary
	blog.update(request.model_dump(), synchronize_session = 'evaluate')
	db.commit()
	# This loads the Blog object from SqlAlchemy's session memory
	# db.refresh(updated_blog) re-fetches the object (in this case - updated_blog) from the DB to ensure:
	#	•	Fields like updated_at that are auto-modified in the DB are now up to date in Python
	# 	•	Any DB-level changes (triggers, calculated fields, etc.) are reflected
	updated_blog = blog.first()
	db.refresh(updated_blog)
	return { 'data': [updated_blog] }

@app.delete('/blogs/{id}', status_code = status.HTTP_200_OK)
def destroy(id: int, _response: Response, db: Session = Depends(get_db)):
    # blog returns a query object which can be chained with other query methods like update, delete etc
    # The query is still not executed until we call .first() or .all()
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'Blog with {id} was not found')
    blog_object = blog.first()
    data = { col.name: getattr(blog_object, col.name) for col in blog_object.__table__.columns }
    blog.delete(synchronize_session = False)
    db.commit()
    return { 'data': [data] }