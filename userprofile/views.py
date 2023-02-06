from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.http import HttpResponseForbidden


from . models import Userprofile,customerProfile
from .forms import UserEditForm, ProfileForm,customerProfileForm,customerCreationForm, Seller_Creation_Form,UserAndProfileForm
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
    orders = Order.objects.filter(items__product__user=request.user)    
    products = request.user.products.exclude(status=Product.DELETED)        
    discounts = Discount.objects.filter(created_by=request.user)
    return render(request, 'userprofile/my_store.html', {
        'products':products,
        'order_items':orders,
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

        session = Session.objects.get(session_key=request.COOKIES["sessionid"])
        uid = session.get_decoded().get('_auth_user_id')        
        user = User.objects.get(pk=uid)
        code=request.GET.get('code','')

        if user:            
            discount= Discount.objects.filter(code_name=code)
            #discount=user.discounts.filter(code_name=request.GET.get('code',''))            
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
                return redirect('discount_view')
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
def add_product(request):
    
    qs = Discount.objects.filter(created_by=request.user)
    if request.method == 'POST':        
        form = ProductForm(request.POST, request.FILES, qs=qs)        
        if form.is_valid():
            title = request.POST.get('title')            
            product = form.save(commit=False)
            product.user = request.user
            product.slug = slugify(title)
            product.save()
            api_own = StripeAPI()
            api_prod, err = api_own.create_product(product)
                
            if err:
                product.delete()
                messages.success(request, f'{err}')
            else:
                product.id_stripe= api_prod.id
                product.save()                    
                messages.success(request, 'The product was added!')
            return redirect ('my_store')
    else:
        form = ProductForm(qs=qs)
    
    return render(request, 'userprofile/product_form.html',{
        'title':'Add',
        'form':form
    })

@login_required
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
        form = ProductForm(instance=product, qs=qs)

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
    u = User.objects.get(pk=request.user.id)
    print(u.customer.stripe_cus_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=u)
        customer_form = customerProfileForm(request.POST)
        if form.is_valid() and customer_form.is_valid():
            form.save()
            #send customer values to stripe API for update customer            
            customer,error = update_customer(str(u.customer.stripe_cus_id),customer_form.cleaned_data)
            redirect('myaccount')
    else:
        form = UserEditForm(instance=u)
        customer, error= retrive_customer(str(u.customer.stripe_cus_id))
        customer_form = customerProfileForm(initial=customer)
            
    return render(request, 'userprofile/myaccount.html', {'form':form, 'customer_form':customer_form})

def customer_signup(request):
    template_name = 'userprofile/signup_customer.html'
    if request.method == 'POST':
        form = customerCreationForm(request.POST)  # UserCreationForm()
        customer_form = customerProfileForm(request.POST)
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
        customer_form = customerProfileForm()
    return render(request,
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
        
    return render(request, 'userprofile/signup.html', {
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