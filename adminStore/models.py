from django.db import models
from store.models import Order, OrderItem
from django.contrib.auth.models import User


class Conversation(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,  related_name='conversation')
    members = models.ManyToManyField(User, related_name='conversations')
    def __str__(self):
        members = ", ".join([str(member) for member in self.members.all()])
        return f"Conversation {self.id}: Order {self.order.id} with members {members}"
    
    
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['conversation']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_read'])
        ]
        ordering = ('created_at',)
    
    def __str__(self):
        return f'{self.conversation.members}'
    
    