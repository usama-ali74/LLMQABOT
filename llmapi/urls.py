from django.urls import path, include
from llmapi.views import LoadStorePDFData, QueryFromRAG, LoadStorePDFDataCelery

urlpatterns = [
    path("load-store-data/", LoadStorePDFData.as_view(), name="load-store-data"),
    path("load-store-data-celery/", LoadStorePDFDataCelery.as_view(), name="load-store-data-celery"),
    path("query-from-bot/", QueryFromRAG.as_view(), name="query-from-bot"),
]
