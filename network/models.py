from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from PIL import Image
from datetime import datetime, timedelta
User = get_user_model()


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    location = models.CharField(max_length=100, blank=True)
    following = models.ManyToManyField('self', blank=True)
    follower_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username

    def save(self):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images', null=True, blank=True)
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ratings = models.ManyToManyField(
        User, through='PostRating', related_name='rated_posts')

    def __str__(self):
        return f'Post by {self.user.username}'


class PostRating(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)


class AccountStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    money_spent = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    jobs_hired = models.PositiveIntegerField(default=0)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    followers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Statistics for {self.user.username}'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)

    def __str__(self):
        return f'Payment by {self.user.username} on {self.payment_date}'


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(
        User, related_name='friend_requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}: {self.status}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)
    description = models.TextField()
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order for {self.service_name} by {self.user.username}'


class JobListing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    skills_required = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)


class Application(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    job_listing = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField()


def default_end_date():
    return datetime.now() + timedelta(days=1)


class Event(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateField(default=datetime.now() + timedelta(days=1))
    end_date = models.DateField(default=datetime.now() + timedelta(days=2))
    description = models.TextField()

    def __str__(self):
        return self.title
