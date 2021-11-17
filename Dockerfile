FROM python:3.9-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY . /code/

RUN pip install -r requirements.txt

CMD ["gunicorn", "giphynavigator.application:app", "-b", "0.0.0.0", "-w", "4", "-k", "uvicorn.workers.UvicornH11Worker"]
