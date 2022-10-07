import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(f'Unsupported file extension. only {" ".join(valid_extensions)}')