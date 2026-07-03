FROM python:3.10

RUN apt-get update && apt-get install -y \
    libzbar0 \
    libgl1 \
    libglib2.0-0

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
