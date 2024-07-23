from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# custom user maneger
class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None):
        """
        Creates and saves a User with the given email, name ,tc and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),  
            name=name,
            tc=tc,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            tc=tc,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# Custom user model
class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="  Email",
        max_length=255,
        unique=True,
    )
    name  = models.CharField(max_length=250)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "tc"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    


CATEGORY_CHOICES=(
    ('BF','Breakfast'),
    ('LH','Lunch'),
    ('DN','Dinner'),
    ('DT','Desert'),
    ('DR','Drinks'),
    ('PT','Platter'),
    ('FF','Fast Food'),
    ('PD','Popular Dishes'),
    ('NA', 'New Arrivals')
)

class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    marked_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')
    prodapp = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to='product')
    def __str__(self):
        return str(self.title)
    
    
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1) 
    
    def __str__(self):
        return str(self.user)
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sender_name = models.CharField(max_length=255)
    receiver_name = models.CharField(max_length=255)
    receiver_email = models.CharField(max_length=255)
    state = models.CharField( max_length=250)
    city = models.CharField(max_length=250)
    locality = models.CharField(max_length=250)
    sender_number =  models.IntegerField(default='')
    receiver_number =  models.IntegerField(default='')

    def __str__(self):
        return self.sender_name

STATUS_CHOICES = {
    ('Pending','Pending'),
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On The Way','On The Way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel'),
}

class OrderPlaced(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    address = models.ForeignKey(Address,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES, default='Pending')
    def __str__(self):
        return str(self.user)