from sqlmodel import Field , SQLModel ,Session , select , create_engine
from datetime import datetime
class User(SQLModel , table=True):
    __tablename__ = "user"
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

engine = create_engine(url="postgresql://root:OMVzj1tCUqSnwH3iZ6WhNz1C@webappdb:5432/postgres" , echo=True) #"sqlite:///./database.db" -  "postgresql://username:pass@postgr:5432/database"
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

