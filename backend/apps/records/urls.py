from django.urls import path
from .views import (
    MedicalRecordListCreateView,
    MedicalRecordDetailView,
    MedicalRecordDownloadView,
    RecordCategoriesView,
)

app_name = 'records'

urlpatterns = [
    path('', MedicalRecordListCreateView.as_view(), name='record-list-create'),
    path('categories/', RecordCategoriesView.as_view(), name='record-categories'),
    path('<str:record_id>/', MedicalRecordDetailView.as_view(), name='record-detail'),
    path('<str:record_id>/download/', MedicalRecordDownloadView.as_view(), name='record-download'),
]
