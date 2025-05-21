from django.urls import path, include
from llmapi.views import LoadStorePDFData, QueryFromRAG

urlpatterns = [
    path("load-store-data/", LoadStorePDFData.as_view(), name="load-store-data"),
    path("query-from-bot/", QueryFromRAG.as_view(), name="query-from-bot"),
]
