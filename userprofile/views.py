from django.views.generic.edit import CreateView,UpdateView
from django.views.generic import DetailView
from django.http import HttpResponse, Http404

from django.contrib import messages
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy

from . models import Userprofile,customerProfile
from .forms import (
    UserEditForm, ProfileForm,customerProfileForm,
    customerCreationForm, customerSignUp,UserAndProfileForm,
)
from store.forms import (
    CarouselImageForm
)
from adminStore.forms import MessageForm
from adminStore.models import Conversation

from django.forms.models import inlineformset_factory
from django.forms import formset_factory

from .api_stripe import *

from store.forms import DiscountForm
from store.models import Discount
from store.decorator import Only_Ajax_Req
from django.db import transaction
from store.forms import ProductForm
from django.forms.models import BaseModelFormSet
from store.models import Product, OrderItem, Order,CarouselImage
from store.decorator import is_vendor
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils.decorators import method_decorator
from django import forms

from django.http import QueryDict


def vendor_detail(request, pk):
    user = User.objects.get(pk=pk)
    products =  user.products.filter(status = Product.ACTIVE)
    return render(request, 'userprofile/vendor_detail.html', {
        'user':user, 
        'products':products,
    })

@is_vendor()
@login_required
def my_store(request):
    
    orders = Order.objects.filter(items__product__user=request.user).distinct()    
    products = request.user.products.exclude(status=Product.DELETED)        
    discounts = Discount.objects.filter(created_by=request.user)
    content = render(request, 'userprofile/my_store2.html', {
        'products':products,
        'orders':orders,
        'discounts':discounts,
    })
    return HttpResponse(content)


@login_required
@is_vendor()
def my_store_order_detail(request, pk):
    orders = Order.objects.filter(items__product__user=request.user).distinct()
    
    order = get_object_or_404(orders, pk=pk)
    conversation = order.conversation.first()
    

    get_total_quantity_per_user= order.get_total_quantity_per_user(request.user)
    get_display_price_per_user=order.get_display_price_per_user(request.user)
    get_display_price_with_discount = order.get_display_price_with_discount(request.user)

    form = MessageForm()
    if request.method=='GET':        
        form = MessageForm(initial={
            'conversation':conversation, 
            'sender':request.user,
            'receiver':order.created_by,
            })
        

    return render(request, 'userprofile/my_store_order_detail.html',{
        'order':order,
        'get_total_quantity_per_user':get_total_quantity_per_user,
        'get_display_price_per_user':get_display_price_per_user,
        'get_display_price_with_discount':get_display_price_with_discount,
        'conversation':conversation,
        'form':form,
    })





@Only_Ajax_Req
@login_required
def check_code_name(request):    
    if request.method == 'GET' and request.is_ajax() and 'sessionid' in request.COOKIES:

        session = Session.objects.get(session_key=request.COOKIES["sessionid"])
        uid = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(pk=uid)
        code=request.GET.get('code','')

        if user:
            #discount= Discount.objects.filter(code_name=code)
            #discount=user.discounts.filter(code_name=request.GET.get('code',''))
            discount, error = get_cupon(code)
            
            if 'valid' in discount and 'percent_off' in discount:
                print(discount.get('valid'))
                print(discount.get('percent_off'))
                data ={'res':'valid', 'percent':discount.get('percent_off')}
            else:
                 data = {'res':'invalid'} 
            return JsonResponse(data, content_type='application/json')
    return JsonResponse({},status=400)


class AddDiscount_CreateView(CreateView):
    model = Discount
    form_class = DiscountForm
    context_object_name = 'discounts'
    template_name = 'userprofile/inventory/EditDiscount.html'
    success_url = reverse_lazy('MyProducts_ListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['form']= DiscountForm(initial={'created_by':self.request.user})
        return context

    def get_success_url(self):
        url = super().get_success_url()
        query_dict =QueryDict(mutable=True)
        query_dict.update({'discountTab':'active'})
        return f'{url}?{query_dict.urlencode()}'

class EditDiscount_UpdateView(UpdateView):
    model =Discount
    form_class = DiscountForm
    context_object_name = 'discounts'
    template_name = 'userprofile/inventory/EditDiscount.html'
    success_url = reverse_lazy('MyProducts_ListView')

    def get_success_url(self):
        url = super().get_success_url()
        query_dict =QueryDict(mutable=True)
        query_dict.update({'discountTab':'active'})
        return f'{url}?{query_dict.urlencode()}'

@login_required
@is_vendor()
def discount_view(request):    
    if request.method == 'POST':
        pid = request.POST['id']        
        
        try:
            obj = Discount.objects.get(id=pid)
        except:
            obj = None

        if obj:
            form = DiscountForm(data=request.POST, instance=obj )
        else:            
            form = DiscountForm(data=request.POST)
        if form.is_valid():
            retrive_coupon = get_cupon(form.cleaned_data['code_name'])            
            if 'id' in retrive_coupon[0]:
                code_name = retrive_coupon[0]['id']                
                del_obj, err = delete_cupon(code_name)
                if 'deleted' in del_obj and len(err)==0:
                    print(f'se elimino {code_name}')
                    print('clean ',form.cleaned_data)
            else:
                print('no estaba')
            cupon,error =create_cupon(form.cleaned_data) 
            if len(error)==0:
                form.save()
                return redirect('my_store')
            else:
                messages.error(request,f'{err}')        
    else:
        id = request.GET.get('id', None)
        del_cupon= True if request.GET.get('delete',False) =='True' else False
        if id:
            discount = Discount.objects.get(id=id)
            if del_cupon:
                del_obj, err = delete_cupon(discount.code_name)
                if 'deleted' in del_obj and len(err)==0:
                    if del_obj.get('deleted',False):
                        discount.delete()
                else:
                    messages.error(request,f'{err}')
                return redirect('discount_view')
            form = DiscountForm(instance=discount)
        else:
            form = DiscountForm(initial={'created_by':request.user})
    discounts = Discount.objects.filter(created_by=request.user)
    return render(request, 'userprofile/inventory/discount.html', {
        'form':form,
        'discounts':discounts
    })

@login_required
@is_vendor()
def add_product(request):
    
    qs = Discount.objects.filter(created_by=request.user)    
    CarouselImageFormSet = formset_factory(CarouselImageForm, extra=1, min_num=1)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, qs=qs)
        carouselFormSet = CarouselImageFormSet(request.POST, request.FILES)

        if form.is_valid():

            title = request.POST.get('title')            
            product = form.save(commit=False)
            product.user = request.user
            product.slug = slugify(title)
            product.save()

            
            if carouselFormSet.is_valid():
                with transaction.atomic():            
                    for formset in carouselFormSet.cleaned_data:                
                        if not all([not formset.get('image')]):
                            image = formset.get('image')
                            caption = formset.get('caption')
                            order = carouselFormSet.cleaned_data.index(formset) + 1
                            CarouselImage.objects.create(
                                product=product, 
                                image=image, 
                                caption=caption, 
                                order=order
                            )
            api_own = StripeAPI()
            api_prod, err = api_own.create_product(product)
                
            if err:
                product.delete()
                messages.error(request, f'{err}')
            else:
                product.id_stripe= api_prod.id
                product.save()                    
                messages.success(request, 'The product was added!')
            return redirect ('my_store')
    else:        
        form = ProductForm(qs=qs)
        carouselFormSet = CarouselImageFormSet()
    return render(request, 'userprofile/product_form.html',{
        'title':'Add',
        'form':form,
        'carouselFormSet':carouselFormSet,
    })



@method_decorator(is_vendor(), name='dispatch')
class MyStore_Order_DetailView(LoginRequiredMixin,DetailView):
    model = Order
    form_class= MessageForm
    template_name = 'userprofile/my_store_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['get_total_quantity_per_user']     = self.object.get_total_quantity_per_user(self.request.user)
        context['get_display_price_per_user']      = self.object.get_display_price_per_user(self.request.user)
        context['get_display_price_with_discount'] = self.object.get_display_price_with_discount(self.request.user)
        context['conversation'] = self.object.conversation.first()
        
        if self.request.method=='GET':        
            context['form'] = MessageForm(initial={
            'conversation':self.object.conversation.first(), 
            'sender':self.request.user,
            'receiver':self.object.created_by,
            })
        
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(items__product__user=self.request.user).distinct()
        return queryset

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.items.filter(product__user=self.request.user).exists():
            return obj
        else:
            raise Http404("Order does not exist for this user")
        
    def post(self,request,*args,**kwargs):
        order = self.get_object()
        conversation = Conversation.objects.filter(order=order).first()
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = self.request.user
            message.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors})




CarouselImageFormSet = inlineformset_factory(Product, CarouselImage, CarouselImageForm,fields=('image', 'caption', 'order'),extra=1, can_delete=False)
@method_decorator(is_vendor(), name='dispatch')
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    
    form_class = ProductForm
    template_name = 'userprofile/product_update.html'
    success_url = reverse_lazy('MyProducts_ListView')
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        self.object = obj
        return obj
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['qs'] = Discount.objects.filter(created_by=self.request.user) 
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(ProductUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['carousel_formset'] = CarouselImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['carousel_formset'] = CarouselImageFormSet(instance=self.object, queryset=self.object.carousel.all())            
        return data

    def get_success_url(self):
        url = super().get_success_url()
        query_dict =QueryDict(mutable=True)
        query_dict.update({'productTab':'active'})
        return f'{url}?{query_dict.urlencode()}'


    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = self.get_form()
        carousel_formset = CarouselImageFormSet(request.POST,request.FILES, instance=product)

        if 'image' in request.FILES:
            x = str(form.instance.thumbnail)
            if not x.replace(form.instance.thumbnail.field.upload_to, '') == str(request.FILES['image']):
                form.instance.thumbnail = None
        
        if form.is_valid() and carousel_formset.is_valid():
            return self.form_valid(form, carousel_formset,self.object)
        else:
            return self.form_invalid(form, carousel_formset)
        

    def validate_api(self, obj):
        #here we delete or archive product and create another        
        api_own= StripeAPI()
        del_prod, err = api_own.delete_product(str(obj.id_stripe))
        if err:                        
            return f'err'
        
        api_edit_prod, err= api_own.create_product(obj)
        if err:                            
            return f'err'
        return None

    def form_valid(self, form, carousel_formset, obj):
        
        err = self.validate_api(obj)
        if err:
            messages.error(self.request, err)
            return self.form_invalid(form, carousel_formset)
        
        context = self.get_context_data()
        carousel_formset = context['carousel_formset']
        with transaction.atomic():
            obj = form.save()

            if carousel_formset.is_valid():
                carousel_formset.instance = obj
                carousel_formset.save()

        return super(ProductUpdateView, self).form_valid(form)
    
    def form_invalid(self, form, carousel_formset):
        return self.render_to_response(
            self.get_context_data(form=form, carousel_formset=carousel_formset)
        )
    

@login_required
@is_vendor()
def edit_product(request, pk):
    if not request.user.has_perm("store.change_product"):
        return HttpResponseForbidden("You don't have permission to edit Product.")
    try:
        product = Product.objects.filter(user=request.user).get(pk=pk)
        
    except Product.DoesNotExist:
        messages.error(request, 'The product you are trying to edit does not exist.')
        return redirect('my_store')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        #remove instance thumbnail to remake the thumbnail in the model 
        if 'image' in request.FILES:
            x = str(form.instance.thumbnail)
            if not x.replace(form.instance.thumbnail.field.upload_to, '') == str(request.FILES['image']):
                form.instance.thumbnail =None        
                print(request.FILES['image'])
                
        if form.is_valid():
            product = form.save(commit=False)
            product.save()                
            
            #here we delete or archive product and create another
            api_own= StripeAPI()
            del_prod, err = api_own.delete_product(str(product.id_stripe))
            if err:
                #the product id was not archived
                print('the product id was not archived', product.id_stripe)
                return redirect('my_store')
            
            api_edit_prod, err= api_own.create_product(product)            
            if err:                
                messages.error(request, f'{err}')
                return redirect('my_store')
            
            product.id_stripe=api_edit_prod.id
            product.save()
            messages.success(request,f'Product {product.title} modified')
            return redirect ('my_store')
    else:
        qs = Discount.objects.filter(created_by=request.user)
        CarouselImageFormSet = formset_factory(CarouselImageForm, extra=4)
        carouselFormSet = CarouselImageFormSet()
        form = ProductForm(instance=product, qs=qs)
        carousel_images = product.carousel.all()
        

    return render(request, 'userprofile/product_form.html',{
        'title':'Edit',
        'product':product,
        'form':form,
        'carouselFormSet':carouselFormSet
    })

@login_required
@is_vendor()
def delete_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)
    product.status = Product.DELETED
    product.save()
    
    id = str(product.id)
    api_own = StripeAPI()
    api_prod, err = api_own.delete_product(id)
    if err:
        print('product deleted', err)
    else:
        messages.success(request, 'The product was deleted!')
    return redirect('my_store')

@login_required
def myaccount(request):
    try:
        u = User.objects.get(pk=request.user.id)        
        
        customer, error= retrive_customer(str(u.customer.stripe_cus_id))
    except Exception as e:
        messages.error(request,f"An error ocurred while retrive the customer {e}")
        return redirect('myaccount')

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=u)
        customer_form = customerProfileForm(request.POST,instance=u.customer)
        if form.is_valid() and customer_form.is_valid():
            form.save()
            
            #send customer values to stripe API for update customer
            # there is not needs to update the customerProfileForm with the user and cus_id_stripe cus are not needed
            customer,error = update_customer(str(u.customer.stripe_cus_id),customer_form.cleaned_data)
        
            if error:
                messages.error(request, f"An error occurred while updating customer information: {error}")
            else:
                messages.success(request, "Your account information has been updated successfully.")
                return redirect('myaccount')
    else:

        form = UserEditForm(instance=u)
        
        customer_form = customerProfileForm(instance=u.customer, initial=customer)
        
    return render(request, 'userprofile/myaccount.html', {'form':form, 'customer_form':customer_form})

def customer_signup(request):
    template_name = 'userprofile/signup_customer.html'
    if request.method == 'POST':
        form = customerCreationForm(request.POST)  
        customer_form = customerSignUp(request.POST)
        if form.is_valid() and customer_form.is_valid():
            client_id, error = create_customer(form.cleaned_data, customer_form.cleaned_data)
            if client_id:
                customer = form.save()
                user = customerProfile.objects.create(stripe_cus_id=client_id, user=customer)
                authenticated_user = authenticate(username=customer, password=form.cleaned_data['password1'])
                if authenticated_user:
                    login(request, authenticated_user)
                return redirect('frontpage')
    else:
        form = customerCreationForm()
        customer_form = customerSignUp()
    return render(
            request,
            template_name,
            {
                'form': form,
                'customer_form': customer_form
            }
        )



def sigup(request):
    if request.method == 'POST':
        
        form =UserAndProfileForm(request.POST)        
        if form.is_valid():            
            user=form.save()            
            authenticated_user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if authenticated_user:                
                login(request, authenticated_user)
                return redirect('frontpage')
    else:        
        form= UserAndProfileForm()
        
    return render(request, 'userprofile/signupVendor.html', {
        'form':form,
        #'profile_form':profile_form
    })



class create_customer_already_signup(UpdateView):
    model = User
    fields = '__all__'
    template_name = 'userprofile/customers/customer.html'
    login_url = 'login'
    #success_url='/' #this is used only if we want static url redirect in class
    
    def get_success_url(self):        
        url='/'
        if self.success_url!='':
            url =self.success_url        
        return url

    def post(self, request, *args, **kwargs):
        form=UserEditForm(request.POST,instance=self.get_object())
        customer_form = customerProfileForm(request.POST)
        self.success_url=request.POST['next']
        if form.is_valid() and customer_form.is_valid():
            self.object=self.get_object()            
            client_id, error = create_customer(form.cleaned_data , customer_form.cleaned_data)
            if client_id:
                user=form.save()
                customer = customerProfile.objects.get(user=user)
                customer.stripe_cus_id=client_id
                customer.save()
            if error!='':
                messages.error(request,error)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form =UserEditForm(instance=self.object)
        customer_form = customerProfileForm()

        '''
        here we only get used the succes_url class varable for add the next field context 
        the @verify_customer decorator takes care of passing the path that the user targets before the form are full fill
        '''
        if request.GET.get('next','') !='':
            self.success_url=request.GET.get('next','')

        context = self.get_context_data(next=self.success_url, object=self.object, form=form, customer_form=customer_form)
        return self.render_to_response(context)

class CustomerUpdateView(UpdateView):    
    model = User
    fields = '__all__'
    template_name = 'userprofile/customers/customer.html'
    login_url = 'login'
    success_url='/'
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form =UserEditForm()
        customer_form = customerProfileForm()
        
        customer, error= retrive_customer(str(self.object.customer.stripe_cus_id))
        
        if error!='':
            messages.error(request,error)
        else:
            form =UserEditForm(instance=self.object)
            customer_form = customerProfileForm(initial=customer)

        context = self.get_context_data(object=self.object, form=form, customer_form=customer_form)
        return self.render_to_response(context)
        
    
    def post(self, request, *args, **kwargs):
        form=UserEditForm(request.POST,instance=self.get_object())
        customer_form = customerProfileForm(request.POST)
                
        if form.is_valid() and customer_form.is_valid():
            self.object=self.get_object()
            customer,error = update_customer(str(self.object.customer.stripe_cus_id),customer_form.cleaned_data)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)