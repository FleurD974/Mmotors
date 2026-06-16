from django.utils import timezone

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, HttpResponseForbidden
from store.models import Car, Application, Document, DocumentType
from store.forms import DocumentForm


def index(request):
    return render(request, 'store/index.html')

def car_detail(request, slug):
    car = get_object_or_404(Car, slug=slug)
    return render(request, 'store/detail.html', context={"car": car})

def all_leased_cars(request):
    cars = Car.objects.filter(is_leased=True)
    return render(request, 'store/leasedOffers.html', context={"cars": cars})
    
def all_purchased_cars(request):
    cars = Car.objects.filter(is_purchased=True)
    print(cars.query)
    return render(request, 'store/purchasedOffers.html', context={"cars": cars})

@login_required
def create_application(request, slug):
    user = request.user
    car = get_object_or_404(Car, slug=slug)
    application, created = Application.objects.get_or_create(customer=user, car=car)

    if application.status != 'draft':
        return HttpResponseForbidden("Already submitted")

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

