from email.policy import default
from pickle import TRUE
from django.db import models
from django.contrib.auth.models import User

class Userprofile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile', on_delete= models.CASCADE)
    is_vendor =models.BooleanField(default=False)
    RFC = models.CharField(max_length=13,blank=True)
    def __str__(self):
        return self.user.username