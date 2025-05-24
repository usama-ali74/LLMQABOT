# myapp/tasks.py
from celery import shared_task
import pandas as pd
from .utils import create_vector_store
from langchain.text_splitter import CharacterTextSplitter

@shared_task
def process_csv_and_create_vector_store(file_path):
    try:
        df = pd.read_csv(file_path)

        text = ""
        for _, row in df.iterrows():
            text += " ".join([str(cell) for cell in row]) + "\n"

        splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
        docs = splitter.create_documents([text])
        create_vector_store(docs)
        return "Success"
    except Exception as e:
        return str(e)
