from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _
from .validators import CustomPasswordValidator
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('visitor', 'Visitor'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='visitor')
    email = models.EmailField(unique=True) 
    
    # password = models.CharField(
    #     max_length=128,
    #     validators=[
    #         MinLengthValidator(8),  # Ensures minimum length
    #         CustomPasswordValidator  # Ensures complexity rules
    #     ]
    # )

    # Fixing the clashes by setting unique related_names
    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)

    def __str__(self):
        return self.username


# Visitor Pre-Registration Model
class VisitorPreRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    purpose = models.CharField(max_length=200)
    host = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    qr_code_data = models.CharField(max_length=255, unique=True, blank=True, null=True)  # Store QR code data
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name


class Visitor(models.Model):
    STATUS_CHOICES = [
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('pending', 'Pending'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="visitor_profile")
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message=_("Phone number must be in format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=15, unique=True)
    
    company_name = models.CharField(max_length=255, blank=True, null=True)
    purpose_of_visit = models.TextField()
    date_of_visit = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    
    pre_registration = models.ForeignKey(
        VisitorPreRegistration, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="visitors"
    )

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        # Generate QR code only if the visitor is new or details have changed
        if not self.pk or any(field in kwargs.get('update_fields', []) for field in ['full_name', 'email', 'purpose_of_visit']):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            # Include a unique identifier (visitor ID) in the QR code data
            qr_data = f"Visitor ID: {self.id}\nName: {self.full_name}\nEmail: {self.email}\nPurpose: {self.purpose_of_visit}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            filename = f"{self.full_name}_qr.png"
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

# Asset Model
class Asset(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Assigned', 'Assigned'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Retired', 'Retired'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Available')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_assets")
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='asset_qr_codes/', blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Generate QR code only if the asset is new or details have changed
        if not self.pk or any(field in kwargs.get('update_fields', []) for field in ['name', 'category', 'status', 'assigned_to']):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = f"Asset: {self.name}\nCategory: {self.category}\nStatus: {self.status}\nAssigned To: {self.assigned_to}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            filename = f"{self.name}_qr.png"
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)
# Report Model
class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_report_type_display()} Report - {self.date}"

    # Dynamic properties to calculate values
    @property
    def visitors(self):
        """Total number of visitors for the report date."""
        return Visitor.objects.filter(date_of_visit=self.date).count()

    @property
    def checked_in(self):
        """Number of visitors checked in for the report date."""
        return Visitor.objects.filter(date_of_visit=self.date, status='checked_in').count()

    @property
    def checked_out(self):
        """Number of visitors checked out for the report date."""
        return Visitor.objects.filter(date_of_visit=self.date, status='checked_out').count()

    @property
    def assets_issued(self):
        """Number of assets issued for the report date."""
        return Asset.objects.filter(created_at__date=self.date, status='Assigned').count()

    @property
    def assets_returned(self):
        """Number of assets returned for the report date."""
        return Asset.objects.filter(created_at__date=self.date, status='Available').count()