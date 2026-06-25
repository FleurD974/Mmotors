from django.utils import timezone

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, HttpResponseForbidden
from accounts.models import Customer
from store.models import Car, Application, Document, DocumentType
from store.forms import DocumentForm, CarForm


def index(request):
    return render(request, 'store/index.html')

def car_detail(request, slug):
    car = get_object_or_404(Car, slug=slug)
    return render(request, 'store/detail.html', context={"car": car})

def all_leased_cars(request):
    cars = Car.objects.filter(is_leased=True, is_available=True)
    return render(request, 'store/leasedOffers.html', context={"cars": cars})
    
def all_purchased_cars(request):
    cars = Car.objects.filter(is_purchased=True, is_available=True)
    return render(request, 'store/purchasedOffers.html', context={"cars": cars})

@login_required
def create_application(request, slug):
    user: Customer = request.user
    user.create_application(slug=slug)

    return redirect('application-detail')

@login_required
def upload_document(request, application_id):
    application = get_object_or_404(Application, id=application_id)  

    if application.customer != request.user:
        return HttpResponseForbidden()

    if application.status != 'draft':
        # remplacer par un message a lecran plutot
        return HttpResponseForbidden("Dossier déjà soumis")

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():
            document = form.save(commit=False)
            document.application = application
            for doc in application.documents.all():
                if doc.type == document.type:
                    messages.add_message(request, messages.ERROR, "Un document de ce type a deja ete ajoute")
                    return redirect('application-detail')

            document.save()
            messages.add_message(request, messages.INFO, "Document ajoute avec succes")
        return redirect('application-detail')

    form = DocumentForm()
    return render(request, 'store/upload.html', context={"application": application, "form": form})

@login_required
def submit_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if application.customer != request.user:
        return HttpResponseForbidden()
    
    application.status = 'submitted'
    application.save()
    messages.add_message(request, messages.INFO, "Application soumise avec succès")
    return redirect('application-detail')

@login_required
def application_detail(request):
    application = get_object_or_404(Application, customer=request.user)
    missing_document_type = DocumentType.objects.exclude(
        id__in=application.documents.values_list('type_id', flat=True)
    )

    if application.status == 'submitted':
        messages.add_message(request, messages.INFO, "Application deja soumise")

    return render(request, 'store/application.html', {
        'application': application,
        'documents': application.documents.all(),
        'missingDocuments': missing_document_type
    })

@staff_member_required
def all_applications(request):
    #access to all application
    applications = Application.objects.filter(status='submitted')
    return render(request, 'store/applications.html', context={"applications": applications})

@staff_member_required
def all_cars(request):
    cars = Car.objects.all()
    return render(request, 'store/allcars.html', context={"cars": cars})

@staff_member_required
def modify_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            car = form.save(commit=False)

            if car.is_purchased and car.is_leased:
                messages.error(
                    request,
                    "Une voiture ne peut pas être en location et à l'achat"
                )
                return redirect('modify-car', car_id=car.id)

            car.save()
            messages.success(
                    request,
                    "Informations modifiées avec succès"
                )
            return redirect('modify-car', car_id=car.id)
    else:
        form = CarForm(instance=car)

    return render(request, 'store/modifycar.html', context={"car": car, "form": form})

@staff_member_required
def add_car(request):
    if request.method == "POST":
        form = CarForm(request.POST)

        if form.is_valid():
            car = form.save(commit=False)

            if car.is_purchased and car.is_leased:
                messages.error(
                    request,
                    "Une voiture ne peut pas être en location et à l'achat"
                )
            else:
                car.save()
                messages.success(
                    request,
                    "Voiture ajoutée avec succès"
                )
                return redirect('all-cars')

    else:
        form = CarForm()

    return render(request, 'store/addcar.html', {"form": form})

@staff_member_required
def admin_application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    documents = application.documents.all()
    return render(
        request,
        'store/review.html',
        {'application': application, 'documents': documents}
    )

@staff_member_required
def approve_application(request, application_id):
    # to approve application
    application = get_object_or_404(Application, id=application_id)

    if application.status != 'submitted':
        return HttpResponseForbidden("Dossier non soumis")

    application.status = 'approved'
    application.reviewed_at = timezone.now()
    car = application.car
    car.is_available = False
    car.save()
    application.save()

    applications = Application.objects.all()
    return render(request, 'store/applications.html', context={"applications": applications})

@staff_member_required
def reject_application(request, application_id):
    # to approve application
    application = get_object_or_404(Application, id=application_id)

    if application.status != 'submitted':
        return HttpResponseForbidden("Dossier non soumis")

    application.status = 'rejected'
    application.reviewed_at = timezone.now()
    application.save()

    applications = Application.objects.all()
    return render(request, 'store/applications.html', context={"applications": applications})

@login_required
def view_document(request, document_id):
    doc = get_object_or_404(Document, id=document_id)

    if doc.application.customer != request.user and not request.user.is_staff:
        return HttpResponseForbidden()

    return FileResponse(doc.file.open('rb'), as_attachment=False)
