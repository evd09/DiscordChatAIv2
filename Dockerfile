FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# right after installing requirements
RUN python3 -m pip show discord.py
RUN python3 -c "import discord; print('discord.py version:', discord.__version__, 'has Bot?', hasattr(discord,'Bot'))"

RUN python3 -m textblob.download_corpora

COPY . .

CMD ["python3", "bot.py"]
