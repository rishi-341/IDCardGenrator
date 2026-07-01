from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.home,             name='home'),
    path('upload/',                 views.upload,           name='upload'),
    path('map-fields/',             views.map_fields,       name='map_fields'),
    path('preview/',                views.preview,          name='preview'),
    path('edit-row/<int:idx>/',     views.edit_row,         name='edit_row'),
    path('save-row/',               views.save_row,         name='save_row'),
    path('design/',                 views.design_select,    name='design_select'),
    path('generate/',               views.generate,         name='generate'),
    path('generating/',             views.generating,       name='generating'),
    path('result/',                 views.result,           name='result'),
    path('download-pdf/',           views.download_pdf,     name='download_pdf'),
    path('view-pdf/',               views.view_pdf,         name='view_pdf'),
    path('clear-cache/',            views.clear_cache,      name='clear_cache'),
    path('api/row-data/<int:idx>/', views.api_row_data,     name='api_row_data'),
]
