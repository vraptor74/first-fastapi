from fastapi import FastAPI, Response,status,HTTPException,Depends,APIRouter
from  sqlalchemy.orm import Session
from  sqlalchemy import func
from app import oauth2
from ..database import get_db
from .. import models,schemas,utils,oauth2
from typing import List, Optional

router = APIRouter(prefix="/posts",tags=['Posts'])

@router.get("/",response_model=List[schemas.PostOut])
def get_posts(db:Session = Depends(get_db),user_id:int = Depends(oauth2.get_current_user),limit : int = 10,skip:int = 0,search: Optional[str] = ""):


    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    #cursor.execute(""" SELECT * FROM posts""")
    #posts  = cursor.fetchall()
    posts =db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts


@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(post:schemas.PostCreate,db:Session = Depends(get_db),get_current_user:int = Depends(oauth2.get_current_user),current_user:int = Depends(oauth2.get_current_user)):
    
    # cursor.execute(""" INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *""",(post.title,post.content,post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    
    new_post = models.Post(owner_id = current_user.id,**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post




@router.get('/{id}',response_model=List[schemas.PostOut])
def get_post(id:int,db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    #cursor.execute("""SELECT * FROM posts WHERE id = %s """,(str(id)))
    #post = cursor.fetchone()
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"post with id: {id} was not found")
    
    return {post}

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    
    post = deleted_post.first()
    
    #cursor.execute("""DELETE FROM posts WHERE id = %s returning *""",(str(id)))
    #deleted_post = cursor.fetchone()
    #conn.commit()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action") 
    deleted_post.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# title str, content string

@router.put("/{id}",response_model=schemas.Post)
def update_post(id:int,updated_post: schemas.PostCreate,db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    #cursor.execute("""UPDATE posts SET title = %s,content = %s,published = %s WHERE id = %s RETURNING *"""  ,(post.title,post.content,post.published,str(id)))
    #conn.commit()
    #updated_post = cursor.fetchone()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action") 
    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()
    return  post_query.first()