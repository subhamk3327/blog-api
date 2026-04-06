'''blog api'''
import psycopg2
from fastapi import FastAPI, HTTPException, Depends
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone, timedelta

load_dotenv()

app = FastAPI()
secret_key = os.getenv("SECRET_KEY")
algo = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = ["auto"])
oauth_scheme= OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise Exception("url not set")
    conn = psycopg2.connect(db_url)
    return conn

class post_c(BaseModel):
    heading : str
    content : str
    username : int

class user_c(BaseModel):
    username : str
    password : str

class comments_c(BaseModel):
    message : str
    username : str

class likes_c(BaseModel):
    likes : int
    username : str

#POSTS
@app.get("/post")#since this is a blog posts are public
def get_posts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from post")
    rows = cursor.fetchall()
    conn.close()
    return [{"id" : row[0],"heading":row[1], "content": row[2], "userid" : row[3]} for row in rows] 

@app.post("/post")# new feature posts automatically correct user_id to its user via token, only registered users can post
def post_posts(new_post : post_c,token : str = Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token,secret_key,algorithms=[algo])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401,detail="invalid token")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from users where username=%s",(username,))
    fetch_user= cursor.fetchone()
    if fetch_user is None:
        raise HTTPException(status_code=401,detail="idk how it reached here but username or password invalid")
    cursor.execute("insert into post(heading,content,user_id) values (%s,%s,%s)",(new_post.heading,new_post.content,fetch_user[0]))
    conn.commit()
    conn.close()
    return{"message": "posted successfully"}

@app.delete("/post/{post_id}")#only creator of post can delete the post
def delete_posts(post_id: int,token : str = Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token,secret_key,algorithms=[algo])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401,detail="invalid token")
    conn= get_db()
    cursor = conn.cursor()
    cursor.execute("select * from post where id =%s",(post_id,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404,detail="post id not found")
    cursor.execute("select * from users where username=%s",(username,))
    fetch_user= cursor.fetchone()
    if fetch_user is None:
        raise HTTPException(status_code=401,detail="idk how it reached here but username or password invalid")
    if fetch_user[0]== row[3]:
        cursor.execute("delete from post where id = %s",(post_id,))
        conn.commit()
    else:
        raise HTTPException(status_code=401,detail="you cannot delete others post")
    conn.close()
    return{"message": "post deleted successfully"}

@app.put("/post/{post_id}")#will add crash check, if exists already, verifications and jwt later
def change_post(post_id : int, new_post : post_c,token : str = Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token,secret_key,algorithms=[algo])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401,detail="invalid token")
    conn= get_db()
    cursor = conn.cursor()
    cursor.execute("select * from post where id =%s",(post_id,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404,detail="post id not found")
    cursor.execute("update post set heading=%s, content=%s, user_id=%s where id=%s ",(new_post.heading,new_post.content,new_post.username, post_id))
    conn.commit()
    conn.close()
    return {"message": "post edited successfully"}

#COMMENTS
@app.post("/post/{post_id}/comments")
def post_comments(new_comment: comments_c, post_id : int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from post where id =%s",(post_id,))
    value = cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404, detail="post not found to register comment")
    cursor.execute("insert into comments(post_id,username,comment) values(%s,%s,%s)",(post_id, new_comment.username,new_comment.message))
    conn.commit()
    conn.close()
    return {"message": "comment posted successfully"}

@app.get("/post/{post_id}/comments")
def get_comments(post_id:int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from comments WHERE post_id=%s",(post_id,))
    value = cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404, detail="there is no post on that post_id")
    cursor.execute("select * from comments WHERE post_id=%s",(post_id,))
    rows= cursor.fetchall()
    conn.close()
    return [{"id": row[0],"post_id" : row[4],"username": row[1], "comment":row[2]} for row in rows]

@app.delete("/post/{post_id}/comments/{comment_id}")
def delete_comments(post_id:int,comment_id:int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from post where id=%s",(post_id,))
    value= cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404,detail="post id not found")
    cursor.execute("select * from comments where id=%s",(comment_id,))
    value= cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404,detail="comment under this post_id not found")
    cursor.execute("delete from comments where id=%s",(comment_id,))
    conn.commit()
    conn.close()
    return {"message":"comment deleted under that post"}

@app.put("/post/{post_id}/comments/{comment_id}")
def change_comment(post_id:int,comment_id:int,new_comment:comments_c):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from post where id=%s",(post_id,))
    value= cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404,detail="post id not found")
    cursor.execute("select * from comments where id=%s",(comment_id,))
    value= cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404,detail="comment under this post_id not found")
    cursor.execute("update comments set comment=%s where id=%s",(new_comment.message,comment_id))
    conn.commit()
    conn.close()
    return {"message": "comment edited successfully"}

# LIKES
@app.post("/post/{post_id}/likes")#need to update user_id mechanism better way
def post_likes(post_id:int,user_id : int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from post where id=%s",(post_id,))
    value= cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404,detail="post id not found")
    cursor.execute("select * from likes where post_id=%s",(post_id,))
    value_check= cursor.fetchone()
    if value_check is None:
        cursor.execute("insert into likes(like_count,post_id,user_id) values(%s,%s,%s)",(1,post_id,user_id))
        conn.commit()
    elif value_check is not None:
        cursor.execute("update likes set like_count=like_count+1, user_id=%s where post_id=%s",(user_id,post_id))
        conn.commit()
        conn.close()
    return {"message":"liked this post successfully"}

@app.get("/post/{post_id}/likes")
def get_likes(post_id:int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from post where id=%s",(post_id,))
    value= cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404,detail="post id not found")
    cursor.execute("select * from likes where post_id=%s",(post_id,))
    rows=cursor.fetchall()
    conn.close()
    return [{"like_id":row[0],"post_id": row[2], "likes":row[1],"user_id":row[3]}for row in rows]

@app.delete("/post/{post_id}/likes")#currently anyone can delete we add userbased deletion later
def delete_likes(post_id: int,):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from post where id=%s",(post_id,))
    value= cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=404,detail="post id not found")
    cursor.execute("select * from likes where post_id=%s",(post_id,))
    values = cursor.fetchone()
    cursor.execute("update likes set like_count= like_count-1 where post_id=%s",(post_id,))
    conn.commit()
    conn.close()
    return {"message": "like delted under this post successfully"}

@app.post("/register")#will add unique userid later
def registration(user : user_c):
    conn = get_db()
    cursor = conn.cursor()
    user.password=pwd_context.hash(user.password)
    cursor.execute("insert into users(username,password) values(%s,%s)",(user.username,user.password))
    conn.commit()
    conn.close()
    return {"sucess":"user registered"}

    
@app.post("/login")
def login(user : user_c):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from users where username=%s",(user.username,))
    value=cursor.fetchone()
    if value is None:
        raise HTTPException(status_code=401,detail="invalid userid or password")
    validation = pwd_context.verify(user.password,value[2])
    if validation is None:
        raise HTTPException(status_code=401,detail="invalid userid or password")
    token = jwt.encode({"sub": value[1],"exp":datetime.now(timezone.utc)+timedelta(minutes=15)},secret_key,algorithm=algo)
    return {"token":token}