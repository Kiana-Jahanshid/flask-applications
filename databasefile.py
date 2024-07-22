from sqlmodel import Field , SQLModel ,Session , select , create_engine
from datetime import datetime

class User(SQLModel , table=True):
    __tablename__ = "users"
    id : int = Field(default=None , primary_key=True)
    username : str = Field(index=True)
    password : str 
    city : str
    first_name : str 
    last_name : str 
    email : str 
    age : int 
    country : str 
    joined_time : str

class Comment(SQLModel , table=True):
    __tablename__ = "comments"
    id : int = Field(default=None , primary_key=True)
    username : str
    user_id : int = Field(foreign_key="users.id") # id of "user table"
    content : str
    time_stamp : datetime = Field(default_factory=datetime.now)

class Comment_ForFaceAnalysis(SQLModel , table=True):
    __tablename__ = "comments_faceanalysis"
    id : int = Field(default=None , primary_key=True)
    username : str
    user_id : int = Field(foreign_key="users.id") # id of "user table"
    content : str
    time_stamp : datetime = Field(default_factory=datetime.now)


# "postgresql://root:OMVzj1tCUqSnwH3iZ6WhNz1C@webappdb:5432/postgres" it's only for deploying in liara 
# "postgresql://username:pass@postgr:5432/database"  --->>  will run on :  http://127.0.0.1:8080/
engine = create_engine(url= "sqlite:///./databasee.db", echo=True) #"sqlite:///./database.db" -  "postgresql://username:pass@postgr:5432/database"
SQLModel.metadata.create_all(engine)


def fetch_user(username):
    with Session(engine) as db_session : 
        query = select(User).where(User.username == username) 
        user = db_session.exec(query).first()
        return user
    
def fetch_all_users():
    with Session(engine) as db_session:
        all_users = select(User)
        all_users = list( db_session.exec(all_users) )
        users_count = Session(engine).query(User).count()
        return all_users , users_count
    
def add_user_to_db(username ,  hashed_password ,city , country ,first_name , last_name , email , age , joined_time):
    with Session(engine) as db_session :#WRITE TO DATABASE
        new_user = User(username=username ,password=hashed_password  , city=city, country=country , first_name= first_name , last_name=last_name , email=email , age=age  ,joined_time=joined_time ) # create a user object
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user) 


def relative_time_from_string(time_string):
    parsed_time = datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
    current_time = datetime.now()
    time_difference = current_time - parsed_time
    seconds = time_difference.total_seconds()
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minutes ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hours ago"
    else:
        days = int(seconds // 86400)
        return f"{days} days ago"


def add_comment_to_db(comment , username , user_id):
    with Session(engine) as db_session:
        new_comment= Comment(content=comment , username=username , time_stamp=datetime.now() , user_id=user_id)
        db_session.add(new_comment)
        db_session.commit()
        db_session.refresh(new_comment)


def add_comment_ToFaceAnalysisDB(comment , username , user_id):
    with Session(engine) as db_session :
        new_comment = Comment_ForFaceAnalysis(content=comment , username=username , user_id=user_id , time_stamp=datetime.now())
        db_session.add(new_comment)
        db_session.commit()
        db_session.refresh(new_comment)


def fetch_comments():
    c = []
    with Session(engine) as db_session:
        # comments = select(Comment.content)
        # all_comments = list( db_session.exec(comments) )
        # for comment in all_comments :
        #     c.append(comment)
        stmt = select(Comment.content, Comment.username)
        all_comments = list( db_session.exec(stmt) )
        return all_comments


def fetch_faceanalysis_comments():
    with Session(engine) as db_session:
        stmt = select(Comment_ForFaceAnalysis.content, Comment_ForFaceAnalysis.username)
        all_comments = list( db_session.exec(stmt) )
        return all_comments
        