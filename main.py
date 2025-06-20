from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

@app.get('/')
def index():
	return { 'data': 'This is the root page' }

@app.get('/about')
def about():
    return { 'data': 'This is the about page' }

@app.get('/blog/unpublished')
def unpublished():
    return { 'data': 'This is the unpublished route' }

@app.get('/blog/{id}')
def show(id: int):
    return { 'data': id }

@app.get('/blog/{id}/comments')
def comments(id: int, limit: int = 10, published: bool = False, optional: Optional[str] = None):
    return { 'data' : f'{id} - {limit} - {published} - {optional}'}

class Blog(BaseModel):
    title: str
    message: str
    published: Optional[str] = None

@app.post('/blog')
def blog(blog: Blog):
    return f'A blog with -> {blog.title} <- and -> {blog.message} <- was created with optional parameter -> {blog.published} <-'
    
