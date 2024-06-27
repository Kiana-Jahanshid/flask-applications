from sqlmodel import Field , SQLModel ,Session , select , create_engine

class User(SQLModel , table=True):
    id : int = Field(default=None , primary_key=True)
    username : str = Field(index=True)
    password : str 
    city : str
    first_name : str 
    last_name : str 
    email : str 
    age : int 
    country : str 


engine = create_engine(url="sqlite:///./database.db" , echo=True)
SQLModel.metadata.create_all(engine)


def fetch_user(username):
    with Session(engine) as db_session : 
        query = select(User).where(User.username == username) 
        user = db_session.exec(query).first()
        return user
    
def add_user_to_db(username ,  hashed_password ,city , country ,first_name , last_name , email , age):
    with Session(engine) as db_session :#WRITE TO DATABASE
        new_user = User(username=username ,password=hashed_password  , city=city, country=country , first_name= first_name , last_name=last_name , email=email , age=age  ) # create a user object
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user) 