from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from . models import Userprofile,customerProfile
from .forms import UserEditForm, ProfileForm,customerProfileForm,customerCreationForm
from .api_stripe import *
from store.forms import DiscountForm
from store.models import Discount
from store.decorator import Only_Ajax_Req

from store.forms import ProductForm
from store.models import Product, OrderItem, Order
from store.decorator import is_vendor
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
def vendor_detail(request, pk):
    user = User.objects.get(pk=pk)
    products =  user.products.filter(status = Product.ACTIVE)
    return render(request, 'userprofile/vendor_detail.html', {
        'user':user, 
        'products':products,
    })

@login_required
def my_store(request):
    products = request.user.products.exclude(status=Product.DELETED)
    order_items = OrderItem.objects.filter(product__user=request.user)
    discounts = Discount.objects.filter(created_by=request.user)
    return render(request, 'userprofile/my_store.html', {
        'products':products,
        'order_items':order_items,
        'discounts':discounts,
    })

@login_required
def my_store_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk )
    
    return render(request, 'userprofile/my_store_order_detail.html',{
        'order':order
    })


@Only_Ajax_Req
@login_required
def check_code_name(request):    
    if request.method == 'GET' and request.is_ajax() and 'sessionid' in request.COOKIES:
        #print('ajoi!!',(request.META))        
        session = Session.objects.get(session_key=request.COOKIES["sessionid"])
        uid = session.get_decoded().get('_auth_user_id')
        #print('aaaaaa',session.get_decoded())
        user = User.objects.get(pk=uid)
        if user:
            
            discount=user.discounts.filter(code_name=request.GET.get('code',''))            
            if len(discount)>0:
                data ={'res':'valid'}
            else:
                data = {'res':'invalid'} 
            return JsonResponse(data)
    return JsonResponse({},status=400)

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
            cupon,error =create_cupon(form.cleaned_data)
            print('aaaaaaaaaaaaaaaa', cupon,error)
            form.save()
        return redirect('discount_view')
    else:
        id = request.GET.get('id', None)
        if id:
            discount = Discount.objects.get(id=id)
            form = DiscountForm(instance=discount)
        else:    
            form = DiscountForm(initial={'created_by':request.user})
        
    discounts = Discount.objects.filter(created_by=request.user)
    return render(request, 'userprofile/inventory/discount.html', {
        'form':form,
        'discounts':discounts
    })
    
@login_required
def add_product(request):
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        print(form.is_valid)
        if form.is_valid():
            title = request.POST.get('title')            
            product = form.save(commit=False)
            product.user = request.user
            product.slug = slugify(title)
            product.save()
            messages.success(request, 'The product was added!')
            return redirect ('my_store')
    else:
        form = ProductForm()
    
    return render(request, 'userprofile/product_form.html',{
        'title':'Add',
        'form':form
    })

@login_required
def edit_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        #remove instance thumbnail to remake the thumbnail in the model 
        if 'image' in request.FILES:
            x = str(form.instance.thumbnail)
            if not x.replace(form.instance.thumbnail.field.upload_to, '') == str(request.FILES['image']):
                #print('xxxxx ',x.replace(form.instance.thumbnail.field.upload_to, ''), '---------', str(request.FILES['image']))
                #print('image' in request.FILES)
                #print(x.replace(form.instance.thumbnail.field.upload_to, ''))
                form.instance.thumbnail =None        
                print(request.FILES['image'])
                
        if form.is_valid():
            form.save()
            messages.success(request, 'The changes was saved!')
            return redirect ('my_store')
    else:    
        form = ProductForm(instance=product)

    return render(request, 'userprofile/product_form.html',{
        'title':'Edit',
        'product':product,
        'form':form
    })

@login_required
def delete_product(request, pk):
    product = Product.objects.filter(user=request.user).get(pk=pk)
    product.status = Product.DELETED
    product.save()
    messages.success(request, 'The product was deleted!')
    return redirect('my_store')

@login_required
def myaccount(request):
    u = User.objects.get(pk=request.user.id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            redirect('myaccount')
    else:
        form = UserEditForm(instance=u)
            
    return render(request, 'userprofile/myaccount.html', {'form':form})

def customer_sigup(request):
    template_name = 'userprofile/sigup_customer.html'
    if request.method == 'POST':
        form =customerCreationForm(request.POST)#UserCreationForm()
        customer_form = customerProfileForm(request.POST)
        if form.is_valid() and customer_form.is_valid():            
            client_id, error = create_customer(form.cleaned_data , customer_form.cleaned_data)
            if client_id:
                customer= form.save()
                user = customerProfile.objects.create(stripe_cus_id=client_id, user=customer)
                if user:
                    login(request, customer)
                    return redirect('frontpage')
    else:
        form =customerCreationForm()
        customer_form = customerProfileForm()
    return render(request, 
        template_name,
        {
        'form':form,
        'customer_form':customer_form
        }
    )


def sigup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)                
        # print(form['username'].value())
        # print(profile_form['is_vendor'].value())
        if form.is_valid():            
            
            user= form.save()
            profile = Userprofile.objects.create(
                user=user, 
                is_vendor=profile_form['is_vendor'].value(),
                RFC=profile_form['RFC'].value()
            )
            if profile:       
                login(request, user)
                return redirect('frontpage')
    else:
        form = UserCreationForm()
        profile_form = ProfileForm()
        
    return render(request, 'userprofile/signup.html', {
        'form':form,
        'profile_form':profile_form
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