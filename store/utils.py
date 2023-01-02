from .models import Discount

def check_code_availabe(code, items):
    cn = Discount.objects.get(code_name=code)
    
    print('items',items)
    return ''