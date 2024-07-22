# Face Analysis Website

its a website , containing :
+ Image Classifocation
+ Face Analysis 
+ Pose Detection
+ ... 


### Using Docker Compose (4.7):

instead of runnig these 3 below commands :
```
related to 4.6 commit :

docker network create mynetwork
docker run  --network mynetwork --name postgr -e POSTGRES_PASSWORD=pass -e POSTGRES_USER=username -e POSTGRES_DB=database -d postgres
docker run -v ./app -p 8080:5000 --network mynetwork webapp
```
we want to use docker compose , to create multiple containers . <br>
so , we should use ```docker-compose.yml``` file . <br>
Now , we only run ```docker compose up -d ``` . 
+ access in local with : http://127.0.0.1:8080

# How to install 

```
pip install -r requirements.txt
```

# How to run 
```
quart --app app run
```

# Result 


+ app link :
```
https://webapplication.liara.run/
```
