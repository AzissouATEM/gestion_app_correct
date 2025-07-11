from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employé'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Client(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Supply(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} de {self.product.name} le {self.date}"

    def save(self, *args, **kwargs):
        # Met à jour automatiquement le stock du produit
        if not self.pk:  # uniquement si nouvelle entrée
            self.product.stock += self.quantity
            self.product.save()
        super().save(*args, **kwargs)


class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Vente #{self.id} - {self.client.name} - {self.date.strftime('%Y-%m-%d %H:%M')}"

    def calculate_total(self):
        total = sum(item.quantity * item.unit_price for item in self.items.all())
        self.total = total
        self.save()


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} à {self.unit_price}"

    def save(self, *args, **kwargs):
        if not self.pk:  # éviter double décompte sur modification
            self.product.stock -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)
        self.sale.calculate_total()
