from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Order
from django.core.mail import send_mail

# When new data is added in order receive a signal
@receiver(post_save, sender=Order)
def on_create_order(sender, instance, created, **kwargs):
    print ('Order created')
    send_mail(
        subject="Checkout Successful! Your Order Was Placed - Kinmel",
        message="Your order was successfully placed and is now being processed.",
        from_email=None, 
        recipient_list=['customer@kinmel.com.np'],
    )