FROM python:3.13


WORKDIR /app


COPY ./requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY . .


CMD ["fastapi", "run", "/app/main.py","--proxy-headers", "--port", "80"]
