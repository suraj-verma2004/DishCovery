from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    home_city = models.CharField(max_length=100, default='Prayagraj')
    pref_veg = models.BooleanField(default=True)

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    locality = models.CharField(max_length=200, null=True, blank=True)
    cuisine = models.CharField(max_length=500)
    phone = models.CharField(max_length=20, null=True, blank=True)
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0) 
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)



class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255) 
    created_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False) 

    def __str__(self):
        return f"Report for {self.restaurant.name} by {self.reported_by.username}"