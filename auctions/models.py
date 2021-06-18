from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    # id, username, email, password are existing fields.
    watchlist = models.ManyToManyField('Listing', related_name="users")
    pass

class Listing(models.Model):
    # 1 user can make multiple listings.
    # multiple users cannot make the same listing.
    # user points to some User.
    # to use related names, the FK we are pointing to can call the related_name variable.
    # Decide not to keep a attribute of a winning user. Use a method in views to fetch the winner user.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    image_url = models.CharField(max_length=512, blank=True)
    category = models.CharField(max_length=128, choices=(
        ("Electronics", "Electronics"),
        ("Books", "Books"),
        ("Others", "Others"),
    ))
    price = models.IntegerField(validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}: ${self.price}"

class Bid(models.Model):
    # users 1 and 2 can bid multiple times on the same listing.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    # one listing can appear multiple times in the Bid table.
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    value = models.IntegerField()

    def __str__(self):
        return f"{self.listing}: {self.user} bid {self.value}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment_text = models.CharField(max_length=1028)

'''Migration in 2 steps: Create instructions on how we want to modify the database,
   Then, take those instructions and apply them to the underlying database.'''
