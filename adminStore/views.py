from .models import Message
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.db.models import Q
from django.contrib.auth.models import Permission,User
from django.contrib.auth.mixins import UserPassesTestMixin

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class AddMessage_CreateView(CreateView):
    model = Message
    

class SavePermisionVendorAPIView(APIView):
    def post(self, request, *args, **kwargs):
        vendor_id = request.data.get('vendorId')
        permission_id = request.data.get('permissionId')
        
        if (request.user.is_staff or request.user.is_superuser) and not (request.user.is_staff and request.user.is_superuser):
            return Response({'error': 'Only staff nor superuser members can access this feature'}, status=status.HTTP_401_UNAUTHORIZED)

        if vendor_id is None or permission_id is None:
            return Response({'error': 'Vendor ID and Permission ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vendor = User.objects.get(pk=vendor_id)            
        except User.DoesNotExist:
            return Response({'error': 'Vendor not found'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            permission = Permission.objects.get(pk=permission_id)
        except Permission.DoesNotExist:
            return Response({'error': 'Permission not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        existing_perm = vendor.user_permissions.filter(id=permission.id).exists()
        if not existing_perm:
            vendor.user_permissions.add(permission)
        else:
            vendor.user_permissions.remove(permission)

        return Response({'success': 'Permission saved for vendor'}, status=status.HTTP_200_OK)

class permissionListView(UserPassesTestMixin, ListView):
    model = Permission
    template_name = 'adminStore/permissionList.html'
    context_object_name = 'permissions'

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):

        return redirect('/')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.request.GET.get('vendor')
        search = self.request.GET.get('search')
        
        if vendor:
            context['vendor_qs']=vendor
            context['vendors'] = User.objects.filter(userprofile__is_vendor=True, username__icontains=search)
        else:
            context['vendors'] = User.objects.filter(userprofile__is_vendor=True)
        return context

    def get_queryset(self):
            
        vendor = self.request.GET.get('vendor')
        queryset = Permission.objects.filter(
            content_type__app_label='store'
        )

        permissions = []
        if vendor:
            try:
                vendor = User.objects.get(id=vendor)
                vendor_perms = [perm.codename for perm in vendor.user_permissions.all()]
                queryset = Permission.objects.filter(content_type__app_label='store')
                for perm in queryset:
                    perm.is_selected = perm.codename in vendor_perms
                    permissions.append(perm)
            except:
                pass
        else:
            permissions = queryset
        
        return permissions