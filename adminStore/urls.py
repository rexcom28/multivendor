from django.urls import path
from . import views

urlpatterns=[
    path('permissions/list/', views.permissionListView.as_view(), name='permissionList'),
    path('api/add-permission/', views.SavePermisionVendorAPIView.as_view(), name='apiSaveVendorPerms'),
]
