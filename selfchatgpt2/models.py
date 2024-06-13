from django.db import models

class History(models.Model):
    datetime = models.DateTimeField()
    query = models.TextField()
    sim1 = models.FloatField()
    sim2 = models.FloatField()
    sim3 = models.FloatField()
    answer = models.TextField()
    
class Chat(models.Model):
    query = models.TextField()
    answer = models.TextField()
