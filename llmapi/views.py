import os
import pandas as pd
from django.conf import settings
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .utils import create_vector_store
from django.http import JsonResponse
from django.core.files.storage import default_storage
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from .tasks import process_csv_and_create_vector_store


class LoadStorePDFData(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES["file"]
        if not file.name.endswith(".csv"):
            return Response(
                {"response": "Please upload the data in csv file type"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            df = pd.read_csv(file)

            text = ""
            for _, row in df.iterrows():
                text += " ".join([str(cell) for cell in row]) + "\n"

            splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
            docs = splitter.create_documents([text])
            create_vector_store(docs)
            return Response({"response": "Data uploaded"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            error_message = str(e)
            return Response(
                {"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QueryFromRAG(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        question = request.data.get("query")
        if not question:
            return JsonResponse({"error": "Please ask your query `query`"}, status=400)
        try:
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.load_local(
                "rag_vectorstore", embeddings, allow_dangerous_deserialization=True
            )

            qa = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(model_name=settings.MODEL_NAME),
                retriever=vectorstore.as_retriever(),
            )

            answer = qa.run(question)
            return Response({"response": answer}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            error_message = str(e)
            return Response(
                {"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoadStorePDFDataCelery(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES["file"]
        if not file.name.endswith(".csv"):
            return Response(
                {"response": "Please upload the data in csv file type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            file_path = default_storage.save(f"uploads/{file.name}", file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # Send task to Celery
            process_csv_and_create_vector_store.delay(full_path)

            return Response({"response": "Data upload initiated"}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
