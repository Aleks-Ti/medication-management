FROM python:3.12

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv
RUN uv export --no-dev --no-hashes | awk '{print $1}' FS=' ;' > requirements.txt

COPY Makefile .


RUN pip install -r requirements.txt --no-cache-dir

COPY ./src ./src

ENV PYTHONPATH=$PYTHONPATH:/src

CMD ["python", "src/main.py"]
