import json
import logging
from django.http import JsonResponse, HttpResponse

# Configure logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib.messages import get_messages
import csv
from django.core.serializers import serialize
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime, timedelta
import qrcode
from PIL import Image, ImageDraw, ImageFont
from .forms import CustomUserCreationForm, VisitorForm, AssetForm, VisitorPreRegistrationForm
from .models import CustomUser, Report, Visitor, Asset, VisitorPreRegistration


logger = logging.getLogger(__name__)

def role_required(*roles):
    """
    Decorator to restrict access to views based on user roles.
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "❌ You do not have permission to access this page.")
                logger.warning(f"Unauthorized access attempt by user {request.user.username}")
                return redirect('VMS:dashboard')
        return wrapper
    return decorator


def user_login(request):
    """
    Handle user login and redirect based on user role.
    """
    if request.user.is_authenticated:
        # Redirect authenticated users based on their role
        if request.user.role == 'admin':
            return redirect('VMS:dashboard')  # Admin dashboard
        elif request.user.role == 'employee':
            return redirect('VMS:assets')  # Employee assets page
        elif request.user.role == 'visitor':
            return redirect('VMS:visitor_dashboard')  # Visitor dashboard
        else:
            return redirect('VMS:dashboard')  # Default fallback

    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()  # Ensure email is lowercase
        password = request.POST.get('password').strip()

        if not email or not password:
            messages.error(request, "❌ Both fields are required.")
            return render(request, 'login.html')

        try:
            # Debugging: Print email and password
            logger.info(f"Attempting login for email: {email}")

            # Fetch the user by email
            user = CustomUser.objects.get(email=email)

            # Debugging: Print user details
            logger.info(f"User found: {user.username}, Role: {user.role}")

            # Authenticate the user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, "✅ Login successful.")
                logger.info(f"User {user.username} logged in successfully.")

                # Generate a badge for visitors
                if user.role == 'visitor':
                    try:
                        visitor = Visitor.objects.get(user=user)
                        badge_response = generate_registration_badge(visitor)
                        return badge_response
                    except Visitor.DoesNotExist:
                        messages.error(request, "❌ Visitor profile not found.")
                        return redirect('VMS:visitor_dashboard')
                    except Exception as e:
                        logger.error(f"Error generating badge: {e}")
                        messages.error(request, "❌ Error generating badge. Please contact support.")
                        return redirect('VMS:visitor_dashboard')

                # Redirect based on user role
                if user.role == 'admin':
                    return redirect('VMS:dashboard')  # Admin dashboard
                elif user.role == 'employee':
                    return redirect('VMS:assets')  # Employee assets page
                elif user.role == 'visitor':
                    return redirect('VMS:visitor_dashboard')  # Visitor dashboard
                else:
                    return redirect('VMS:dashboard')  # Default fallback

            else:
                messages.error(request, "❌ Invalid email or password.")
                logger.warning(f"Failed login attempt for email: {email}")
        except CustomUser.DoesNotExist:
            messages.error(request, "❌ User with this email does not exist.")
            logger.warning(f"Login attempt with non-existent email: {email}")

    return render(request, 'login.html')
def register(request):
    """
    Handle user registration and redirect based on user role.
    """
    if request.user.is_authenticated:
        # Redirect authenticated users based on their role
        if request.user.role == 'admin':
            return redirect('VMS:dashboard')  # Admin dashboard
        elif request.user.role == 'employee':
            return redirect('VMS:assets')  # Employee assets page
        elif request.user.role == 'visitor':
            return redirect('VMS:visitor_dashboard')  # Visitor dashboard
        else:
            return redirect('VMS:dashboard')  # Default fallback

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "✅ Registration successful. Welcome!")
            logger.info(f"New user registered: {user.username}")

            # Log the user in after registration
            user = authenticate(
                request,
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                backend='VMS.backends.EmailBackend'  # Specify the custom backend
            )
            if user is not None:
                auth_login(request, user, backend='VMS.backends.EmailBackend')  # Specify the backend

                # Generate a badge for visitors
                if user.role == 'visitor':
                    try:
                        # Create a Visitor profile for the newly registered visitor
                        visitor = Visitor.objects.create(
                            user=user,
                            full_name=user.get_full_name(),
                            email=user.email,
                            phone_number=form.cleaned_data.get('phone_number', ''),
                            purpose_of_visit="Registration",  # Default purpose
                            status='pending'  # Default status
                        )
                        # Generate and return the badge
                        badge_response = generate_registration_badge(visitor)
                        return badge_response
                    except Exception as e:
                        logger.error(f"Error creating visitor profile: {e}")
                        messages.error(request, "❌ Error generating visitor badge. Please contact support.")
                        return redirect('VMS:visitor_dashboard')

                # Redirect based on user role
                if user.role == 'admin':
                    return redirect('VMS:dashboard')  # Admin dashboard
                elif user.role == 'employee':
                    return redirect('VMS:assets')  # Employee assets page
                elif user.role == 'visitor':
                    return redirect('VMS:visitor_dashboard')  # Visitor dashboard
                else:
                    return redirect('VMS:dashboard')  # Default fallback
            else:
                messages.error(request, "❌ Login failed after registration. Please log in manually.")
        else:
            messages.error(request, "❌ Registration failed. Please correct the errors.")
            logger.warning(f"Form errors: {form.errors}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def user_logout(request):
    """
    Handle user logout.
    """
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    logger.info(f"User {request.user.username} logged out.")
    return redirect('VMS:login')

@login_required
def dashboard(request):
    """
    Render the dashboard with relevant statistics.
    """
    context = {
        'total_visitors': Visitor.objects.count(),
        'active_visitors': Visitor.objects.filter(status='checked_in').count(),
        'total_assets': Asset.objects.count(),
        'assigned_assets': Asset.objects.filter(status='Assigned').count(),
        'recent_visitors': Visitor.objects.order_by('-date_of_visit')[:5],
        'recent_assets': Asset.objects.order_by('-created_at')[:5],
        "user_role": request.user.role,
    }
    return render(request, 'dashboard.html', context)


login_required
@role_required('admin', 'employee')
def assets(request):
    """
    Handle asset management (registration and assignment in one form).
    """
    assets = Asset.objects.all()  # Fetch all assets for the dropdown and table

    if request.method == 'POST':
        if 'asset-form' in request.POST:
            asset_form = AssetForm(request.POST)
            if asset_form.is_valid():
                asset = asset_form.save()
                messages.success(request, "Asset added successfully.")

                # If assigned_to is provided, assign the asset
                assigned_to = asset_form.cleaned_data.get('assigned_to')
                if assigned_to:
                    asset.assigned_to = assigned_to
                    asset.status = 'Assigned'
                    asset.save()
                    messages.success(request, f"Asset assigned to {assigned_to} successfully.")

                return redirect('VMS:assets')
        else:
            messages.error(request, "Invalid form submission.")
    else:
        asset_form = AssetForm()

    context = {
        'assets': assets,
        'asset_form': asset_form,
    }
    return render(request, 'assets.html', context)

def download_asset_qr(request, asset_id):
    """
    Download the QR code for an asset.
    """
    asset = Asset.objects.get(id=asset_id)
    if asset.qr_code:
        response = HttpResponse(asset.qr_code, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{asset.name}_qr.png"'
        return response
    else:
        return HttpResponse("QR code not found.", status=404)

@login_required
@role_required('admin', 'employee')
def edit_asset(request, asset_id):
    """
    View for editing an existing asset.
    """
    asset = get_object_or_404(Asset, id=asset_id)  # Fetch the asset to edit

    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)  # Bind the form to the existing asset
        if form.is_valid():
            form.save()
            messages.success(request, "Asset updated successfully.")
            return redirect('VMS:assets')
    else:
        form = AssetForm(instance=asset)  # Pre-fill the form with the asset's current data

    context = {
        'form': form,
    }
    return render(request, 'edit_asset.html', context)

@login_required
@role_required('admin', 'employee')
def delete_asset(request, asset_id):
    """
    View for deleting an existing asset.
    """
    asset = get_object_or_404(Asset, id=asset_id)  # Fetch the asset to delete

    if request.method == 'POST':
        asset.delete()
        messages.success(request, "Asset deleted successfully.")
        return redirect('VMS:assets')

    context = {
        'asset': asset,
    }
    return render(request, 'confirm_delete_asset.html', context)

@login_required
@role_required('admin', 'employee')
def reports(request):
    """
    Generate and export reports.
    """
    report_type = request.GET.get('report_type', 'daily')
    today = datetime.today().date()

    if report_type == 'daily':
        report = Report(report_type='daily', date=today)
    elif report_type == 'weekly':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        report = Report(report_type='weekly', date=end_of_week)
    elif report_type == 'monthly':
        start_of_month = today.replace(day=1)
        end_of_month = start_of_month.replace(day=28) + timedelta(days=4)  # Handle months with 28-31 days
        report = Report(report_type='monthly', date=end_of_month)
    else:
        report = Report(report_type='daily', date=today)

    # Handle CSV export
    if 'export_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Date', 'Visitors', 'Checked-in', 'Checked-out', 'Assets Issued', 'Assets Returned'])
        writer.writerow([report.date, report.visitors, report.checked_in, report.checked_out, report.assets_issued, report.assets_returned])
        return response

    # Handle PDF export
    if 'export_pdf' in request.GET:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, f"{report.get_report_type_display()} Report - {report.date}")
        y = 730
        p.drawString(100, y, "Date | Visitors | Checked-in | Checked-out | Assets Issued | Assets Returned")
        y -= 20
        p.drawString(100, y, f"{report.date} | {report.visitors} | {report.checked_in} | {report.checked_out} | {report.assets_issued} | {report.assets_returned}")
        y -= 20
        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    return render(request, 'reports.html', {'report': report})


@login_required
@role_required('admin')
def users(request):
    """
    Handle user management.
    """
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "User added successfully.")
            return redirect('VMS:users')
    else:
        user_form = CustomUserCreationForm()

    users = CustomUser.objects.all()
    return render(request, 'users.html', {'users': users, 'user_form': user_form})


@login_required
@role_required('admin')
def edit_user(request, user_id):
    """
    Edit an existing user.
    """
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "User updated successfully.")
            return redirect('VMS:users')
    else:
        user_form = CustomUserCreationForm(instance=user)

    return render(request, 'edit_user.html', {'user_form': user_form, 'user': user})


@login_required
@role_required('admin')
def delete_user(request, user_id):
    """
    Delete a user.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('VMS:users')


@login_required
@role_required('admin', 'employee')
def visitor(request):
    """
    Handle visitor management.
    """
    if request.method == 'POST':
        form = VisitorForm(request.POST, request.FILES)
        if form.is_valid():
            visitor = form.save()
            messages.success(request, "Visitor added successfully.")
            logger.info(f"New visitor added: {visitor.full_name}")

            # Generate and return the badge
            return generate_registration_badge(visitor)

    else:
        form = VisitorForm()

    return render(request, 'visitor.html', {'visitors': Visitor.objects.all(), 'form': form})

def generate_qr_code(request, asset_id):
    """
    Generate a QR code for an asset and return it as an image.
    """
    asset = Asset.objects.get(id=asset_id)
    qr_content = f"""
        Asset ID: {asset.id}
        Name: {asset.name}
        Category: {asset.category}
        Status: {asset.status}
        Assigned To: {asset.assigned_to}
    """

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Return the image as a response
    return HttpResponse(buffer, content_type="image/png")

def generate_registration_badge(instance):
    """
    Generate a registration badge with a QR code for the given instance (Visitor or Asset).
    """
    try:
        # Create a QR code with instance details
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        if isinstance(instance, Visitor):
            qr_data = f"Visitor ID: {instance.id}\nName: {instance.full_name}\nEmail: {instance.email}\nPhone: {instance.phone_number}\nPurpose: {instance.purpose_of_visit}"
        elif isinstance(instance, Asset):
            qr_data = f"Asset ID: {instance.id}\nName: {instance.name}\nCategory: {instance.category}\nStatus: {instance.status}\nAssigned To: {instance.assigned_to}"
        else:
            return HttpResponse("Invalid instance type.", status=400)

        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create an image with the QR code
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Create a badge image
        badge = Image.new('RGB', (400, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(badge)
        font = ImageFont.load_default()

        # Add instance details to the badge
        if isinstance(instance, Visitor):
            draw.text((10, 10), f"Visitor ID: {instance.id}", font=font, fill="black")
            draw.text((10, 40), f"Name: {instance.full_name}", font=font, fill="black")
            draw.text((10, 70), f"Email: {instance.email}", font=font, fill="black")
            draw.text((10, 100), f"Phone: {instance.phone_number}", font=font, fill="black")
            draw.text((10, 130), f"Purpose: {instance.purpose_of_visit}", font=font, fill="black")
        elif isinstance(instance, Asset):
            draw.text((10, 10), f"Asset ID: {instance.id}", font=font, fill="black")
            draw.text((10, 40), f"Name: {instance.name}", font=font, fill="black")
            draw.text((10, 70), f"Category: {instance.category}", font=font, fill="black")
            draw.text((10, 100), f"Status: {instance.status}", font=font, fill="black")
            draw.text((10, 130), f"Assigned To: {instance.assigned_to}", font=font, fill="black")

        # Paste the QR code onto the badge
        badge.paste(qr_img, (50, 150))

        # Save the badge to a BytesIO object
        badge_bytes = BytesIO()
        badge.save(badge_bytes, format='PNG')
        badge_bytes.seek(0)

        # Return the badge as a downloadable response
        response = HttpResponse(badge_bytes, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{instance.__class__.__name__.lower()}_badge_{instance.id}.png"'
        return response

    except Exception as e:
        logger.error(f"Error generating badge: {e}")
        return HttpResponse("Error generating badge. Please try again.", status=500)


def download_badge(request, visitor_id):
    visitor = Visitor.objects.get(id=visitor_id)
    
    # Create PDF badge
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Add content to PDF
    p.drawString(100, 750, f"Visitor Badge: {visitor.user.username}")
    p.drawString(100, 730, f"Email: {visitor.email}")
    p.drawString(100, 710, f"Purpose: {visitor.purpose_of_visit}")
    
    # Add QR code to PDF
    if visitor.qr_code:
        p.drawImage(visitor.qr_code.path, 100, 500, width=200, height=200)
    
    p.showPage()
    p.save()

    # Prepare response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{visitor.user.username}_badge.pdf"'
    return response

def download_asset_badge(request, asset_id):
    """
    Generate and download a badge for an asset with a QR code.
    """
    asset = Asset.objects.get(id=asset_id)
    
    # Create PDF badge
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Add content to PDF
    p.drawString(100, 750, f"Asset Badge: {asset.name}")
    p.drawString(100, 730, f"Category: {asset.category}")
    p.drawString(100, 710, f"Status: {asset.status}")
    p.drawString(100, 690, f"Assigned To: {asset.assigned_to}")
    
    # Add QR code to PDF
    if asset.qr_code:
        p.drawImage(asset.qr_code.path, 100, 500, width=200, height=200)
    
    p.showPage()
    p.save()

    # Prepare response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{asset.name}_badge.pdf"'
    return response

@login_required
@role_required('admin', 'employee')
def edit_visitor(request, visitor_id):
    """
    Edit an existing visitor.
    """
    visitor = get_object_or_404(Visitor, id=visitor_id)

    if request.method == 'POST':
        form = VisitorForm(request.POST, request.FILES, instance=visitor)
        if form.is_valid():
            form.save()
            messages.success(request, "Visitor updated successfully.")
            return redirect('VMS:visitor')
    else:
        form = VisitorForm(instance=visitor)

    return render(request, 'edit_visitor.html', {'form': form, 'visitor': visitor})


@login_required
@role_required('admin', 'employee')
def delete_visitor(request, visitor_id):
    """
    Delete a visitor.
    """
    visitor = get_object_or_404(Visitor, id=visitor_id)
    visitor.delete()
    messages.success(request, "Visitor deleted successfully.")
    return redirect('VMS:visitor')

@login_required
@role_required('visitor')
def visitor_dashboard(request):
    """
    Handle visitor dashboard.
    """
    # Fetch the visitor object for the logged-in user
    visitor = Visitor.objects.filter(user=request.user).first()
    print(visitor)  # Debugging: Print the visitor object
    if visitor:
        print(visitor.qr_code)  # Debugging: Print the QR code field

    if request.method == 'POST':
        # Check if the form is for pre-registration status check
        if 'check_email' in request.POST:
            email = request.POST.get('email', '').strip().lower()

            if email:
                # Check if the visitor is pre-registered
                pre_registered_visitor = VisitorPreRegistration.objects.filter(email__iexact=email).first()
                if pre_registered_visitor:
                    messages.success(request, "✅ You have been pre-registered!")
                else:
                    messages.error(request, "❌ No pre-registration found. Please register.")
            else:
                messages.error(request, "❌ Please enter a valid email address.")

        # Handle new visitor registration
        elif 'register_visitor' in request.POST:
            form = VisitorPreRegistrationForm(request.POST)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "✅ Registration successful!")
                    logger.info(f"New visitor pre-registered: {form.cleaned_data['email']}")
                except Exception as e:
                    logger.error(f"Error saving visitor pre-registration: {e}")
                    messages.error(request, "❌ Registration failed. Please try again.")
            else:
                messages.error(request, "❌ Registration failed. Please correct the errors.")
                logger.warning(f"Form errors: {form.errors}")

    # Render the form
    form = VisitorPreRegistrationForm()
    context = {
        'form': form,
        'visitor': visitor,  # Pass the visitor object to the template
    }
    return render(request, 'visitor_dashboard.html', context)

@csrf_exempt
def check_pre_registration(request):
    """
    Check if a visitor is pre-registered using their email.
    """
    if request.method == 'POST':
        email = request.POST.get("email")  # Get email from form data
        if email:
            is_registered = VisitorPreRegistration.objects.filter(email__iexact=email).exists()
            return JsonResponse({"registered": is_registered})
        else:
            return JsonResponse({"error": "Email is required."}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


def visitor_registration(request):
    """
    Handle visitor pre-registration and generate a QR code.
    """
    if request.method == 'POST':
        form = VisitorPreRegistrationForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            
            # Generate QR code data
            qr_data = f"""
                Visitor Name: {visitor.name}
                Email: {visitor.email}
                Phone: {visitor.phone_number}
                Purpose: {visitor.purpose}
            """
            visitor.qr_code_data = qr_data  # Save QR code data

            # Generate QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Save QR code image to the visitor model
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            visitor.qr_code_image.save(f'{visitor.name}_qr.png', ContentFile(buffer.getvalue()), save=False)

            visitor.save()
            messages.success(request, "Visitor pre-registration submitted successfully!")
            return redirect('VMS:visitor_dashboard')
    else:
        form = VisitorPreRegistrationForm()

    return render(request, 'visitor_registration.html', {'form': form})

def verify_visitor(request):
    return render(request, 'verify_visitor.html')

def welcome_view(request):
    """
    Render the welcome page.
    """
    return render(request, 'Welcome_page.html')