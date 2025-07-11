from django.urls import path
from . import views

app_name = 'app_database'

urlpatterns = [
    path('', views.database_dashboard, name='dashboard'),
    path('get_table/', views.get_table_data, name='get_table'),
    path('delete_row/', views.delete_row, name='delete_row'),
    path('edit_row/', views.edit_row_view, name='edit_row'),
]
