from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.forms import inlineformset_factory
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.db.models.functions import TruncMonth
from django.db.models import Sum

from .models import Employee, Product, Client, Supply, Sale, SaleItem
from .forms import (
    UserForm, EmployeeForm,
    ProductForm, ClientForm, SupplyForm, SaleForm, SaleItemForm
)

User = get_user_model()

from datetime import datetime

@login_required
def home(request):
    from django.db.models.functions import TruncMonth
    from django.db.models import Sum
    import calendar

    sales_qs = (
        Sale.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total'))
        .order_by('month')
    )

    supplies_qs = (
        Supply.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('quantity'))
        .order_by('month')
    )

    # Convertir tous les mois en datetime.date
    def to_date(obj):
        return obj.date() if isinstance(obj, datetime) else obj

    months_sales = {to_date(entry['month']) for entry in sales_qs}
    months_supply = {to_date(entry['month']) for entry in supplies_qs}
    all_months = sorted(months_sales.union(months_supply))

    sales_dict = {to_date(entry['month']): float(entry['total']) for entry in sales_qs}
    supply_dict = {to_date(entry['month']): entry['total'] for entry in supplies_qs}

    sales_data = [sales_dict.get(month, 0) for month in all_months]
    supply_data = [supply_dict.get(month, 0) for month in all_months]

    def format_month_label(dt):
        return f"{calendar.month_abbr[dt.month]} {dt.year}"

    labels = [format_month_label(month) for month in all_months]

    total_sales = Sale.objects.aggregate(total=Sum('total'))['total'] or 0
    total_supplies = Supply.objects.aggregate(total=Sum('quantity'))['total'] or 0

    return render(request, 'core/home.html', {
        'labels': labels,
        'sales_data': sales_data,
        'supply_data': supply_data,
        'total_sales': total_sales,
        'total_supplies': total_supplies,
    })

# --- Le reste de tes vues restent inchangées ---

# ... (rest of the code unchanged)


# --- Le reste de tes vues restent inchangées ---

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect('home')
        else:
            messages.error(request, "Nom d’utilisateur ou mot de passe incorrect.")
    return render(request, 'core/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('login')

# -- Employee Views --

@login_required
def employee_list(request):
    employees = Employee.objects.select_related('user').all()
    return render(request, 'core/employee_list.html', {'employees': employees})

@login_required
@transaction.atomic
def employee_create(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        employee_form = EmployeeForm(request.POST)
        if user_form.is_valid() and employee_form.is_valid():
            user = user_form.save()
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()
            messages.success(request, "Employé ajouté avec succès.")
            return redirect(reverse_lazy('employee_list'))
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        user_form = UserForm()
        employee_form = EmployeeForm()
    return render(request, 'core/employee_form.html', {'user_form': user_form, 'employee_form': employee_form, 'title': 'Ajouter un employé'})

@login_required
@transaction.atomic
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    user = employee.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        employee_form = EmployeeForm(request.POST, instance=employee)
        if user_form.is_valid() and employee_form.is_valid():
            user_form.save()
            employee_form.save()
            messages.success(request, "Employé modifié avec succès.")
            return redirect(reverse_lazy('employee_list'))
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        user_form = UserForm(instance=user)
        employee_form = EmployeeForm(instance=employee)
    return render(request, 'core/employee_form.html', {'user_form': user_form, 'employee_form': employee_form, 'title': 'Modifier un employé'})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.user.delete()
        messages.success(request, "Employé supprimé avec succès.")
        return redirect(reverse_lazy('employee_list'))
    return render(request, 'core/employee_confirm_delete.html', {'employee': employee})

# -- Product Views --

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'core/product_list.html', {'products': products})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect(reverse_lazy('product_list'))
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ProductForm()
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Ajouter un produit'})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès.")
            return redirect(reverse_lazy('product_list'))
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Modifier un produit'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect(reverse_lazy('product_list'))
    return render(request, 'core/product_confirm_delete.html', {'product': product})

# -- Client Views --

@login_required
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'core/client_list.html', {'clients': clients})

@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Client ajouté avec succès.")
            return redirect(reverse_lazy('client_list'))
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ClientForm()
    return render(request, 'core/client_form.html', {'form': form, 'title': 'Ajouter un client'})

@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client modifié avec succès.")
            return redirect(reverse_lazy('client_list'))
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ClientForm(instance=client)
    return render(request, 'core/client_form.html', {'form': form, 'title': 'Modifier un client'})

@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, "Client supprimé avec succès.")
        return redirect(reverse_lazy('client_list'))
    return render(request, 'core/client_confirm_delete.html', {'client': client})

# -- Supply Views --

@login_required
def supply_list(request):
    supplies = Supply.objects.select_related('product').all()
    return render(request, 'core/supply_list.html', {'supplies': supplies})

@login_required
def supply_create(request):
    if request.method == 'POST':
        form = SupplyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Approvisionnement ajouté avec succès.")
            return redirect(reverse_lazy('supply_list'))
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = SupplyForm()
    return render(request, 'core/supply_form.html', {'form': form, 'title': 'Ajouter un approvisionnement'})

@login_required
def supply_update(request, pk):
    supply = get_object_or_404(Supply, pk=pk)
    if request.method == 'POST':
        form = SupplyForm(request.POST, instance=supply)
        if form.is_valid():
            form.save()
            messages.success(request, "Approvisionnement modifié avec succès.")
            return redirect(reverse_lazy('supply_list'))
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = SupplyForm(instance=supply)
    return render(request, 'core/supply_form.html', {'form': form, 'title': 'Modifier un approvisionnement'})

@login_required
def supply_delete(request, pk):
    supply = get_object_or_404(Supply, pk=pk)
    if request.method == 'POST':
        supply.product.stock -= supply.quantity
        supply.product.save()
        supply.delete()
        messages.success(request, "Approvisionnement supprimé avec succès.")
        return redirect(reverse_lazy('supply_list'))
    return render(request, 'core/supply_confirm_delete.html', {'supply': supply})

# -- Sale Views --

@login_required
def sale_list(request):
    sales = Sale.objects.select_related('client').all()
    return render(request, 'core/sale_list.html', {'sales': sales})

@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    items = sale.items.select_related('product').all()
    return render(request, 'core/sale_detail.html', {'sale': sale, 'items': items})

@login_required
@transaction.atomic
def sale_create(request):
    SaleItemFormSet = inlineformset_factory(Sale, SaleItem, form=SaleItemForm, extra=1, can_delete=True)
    if request.method == 'POST':
        sale_form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST)
        if sale_form.is_valid() and formset.is_valid():
            sale = sale_form.save()
            items = formset.save(commit=False)
            for item in items:
                item.sale = sale
                item.save()
            messages.success(request, "Vente créée avec succès.")
            return redirect(reverse_lazy('sale_list'))
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        sale_form = SaleForm()
        formset = SaleItemFormSet()
    return render(request, 'core/sale_form.html', {
        'form': sale_form,
        'formset': formset,
        'title': 'Ajouter une vente'
    })

@login_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        for item in sale.items.all():
            item.product.stock += item.quantity
            item.product.save()
        sale.delete()
        messages.success(request, "Vente supprimée avec succès.")
        return redirect(reverse_lazy('sale_list'))
    return render(request, 'core/sale_confirm_delete.html', {'sale': sale})

@login_required
def sale_invoice_pdf(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    template_path = 'core/sale_invoice.html'
    context = {'sale': sale}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="facture_vente_{sale.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=response, encoding='UTF-8')

    if pisa_status.err:
        return HttpResponse("Une erreur est survenue lors de la génération du PDF", status=500)

    return response
