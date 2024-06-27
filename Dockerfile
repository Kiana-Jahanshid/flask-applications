FROM python

WORKDIR /app

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install opencv-python-headless

COPY . .
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


CMD ["quart", "run", "--port=5000", "--host=0.0.0.0"]