from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, HttpResponseForbidden
from accounts.models import Customer
from store.models import Car, Application, Document, DocumentType
from store.forms import DocumentForm, CarForm

import logging

logger = logging.getLogger('store')

def index(request):
    """
    Display home page.

    Args:
        request (HttpRequest): client HTTP request

    Returns:
        HttpResponse: HTTP Response with template content
        ``store/index.html``.
    """
    return render(request, 'store/index.html')

def about(request):
    """
    Display about page.

    Args:
        request (HttpRequest): client HTTP request

    Returns:
        HttpResponse: HTTP Response with template content
        ``store/about.html``.
    """
    return render(request, 'store/about.html')

def legal_notice(request):
    """
    Display legal notice page.

    Args:
        request (HttpRequest): client HTTP request

    Returns:
        HttpResponse: HTTP Response with template content
        ``store/legal.html``.
    """
    return render(request, 'store/legal.html')

def car_detail(request, slug):
    """
    Display cars detail page from its slug

    Args:
        request (HttpRequest): client HTTP request
        slug (str): Car identifier used in URL

    Returns:
        HttpResponse: HTTP Response with template content
        ``store/detail.html`` with car in context

    Raises:
        Http404: raised if no slug
    """
    car = get_object_or_404(Car, slug=slug)
    return render(request, 'store/detail.html', context={"car": car})

def all_leased_cars(request):
    """
    Display all leased and available cars.

    Args:
        request (HttpRequest): client HTTP request

    Returns:
        HttpResponse: HTTP Response with template content
        ``store/leasedOffers.html`` with car in context
    """
    cars = Car.objects.filter(is_leased=True, is_available=True)
    return render(request, 'store/leasedOffers.html', context={"cars": cars})

def all_purchased_cars(request):
    """
    Display all purchasable and available cars.

    Args:
        request (HttpRequest): client HTTP request

    Returns:
        HttpResponse: HTTP Response with template content
        ``store/purchasedOffers.html`` with cars in context
    """
    cars = Car.objects.filter(is_purchased=True, is_available=True)
    return render(request, 'store/purchasedOffers.html', context={"cars": cars})

@login_required
def create_application(request, slug):
    """
    Create application and redirect to it detail page

    Args:
        request (HttpRequest): client HTTP request
        slug (str): Car identifier used in URL

    Returns:
        HttpResponseRedirect: HTTP Response with template content
        ``application-detail``
    """
    user: Customer = request.user
    user.create_application(slug=slug)

    return redirect('application-detail')

@login_required
def upload_document(request, application_id):
    """
    Handles document upload for a specific application.

    This view allows an authenticated user to upload a document related to
    an application. It enforces access control by ensuring that the requesting
    user is the owner of the application and that the application is still in
    'draft' status.

    On POST requests, the submitted form is validated and the document is
    associated with the application. The view also prevents duplicate document
    types from being added to the same application.

    On success, a success message is displayed and the user is redirected to
    the application detail page. On GET requests, an empty form is rendered.

    Args:
        request (HttpRequest): The HTTP request object containing user and form data.
        application_id (int): The ID of the application to which the document belongs.

    Returns:
        HttpResponse:
            - Redirects to 'application-detail' after successful upload or validation failure.
            - Renders 'store/upload.html' with the upload form on GET requests.

    Raises:
        Http404: If no Application matches the given ID.
        HttpResponseForbidden: If the user is not the owner of the application
            or if the application is not in 'draft' status.
    """
    application = get_object_or_404(Application, id=application_id)

    if application.customer != request.user:
        return HttpResponseForbidden("Vous n'avez pas accès")

    if application.status != 'draft':
        return HttpResponseForbidden("Dossier déjà soumis")

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():
            document = form.save(commit=False)
            document.application = application
            for doc in application.documents.all():
                if doc.type == document.type:
                    messages.add_message(request, messages.ERROR, "Un document de ce type a déjà été ajouté")
                    return redirect('application-detail')

            document.save()
            messages.add_message(request, messages.INFO, "Document ajouté avec succès")
        return redirect('application-detail')

    form = DocumentForm()
    return render(request, 'store/upload.html', context={"application": application, "form": form})

@login_required
def submit_application(request, application_id):
    """
    Submit logged user application

    Allows an authenticated user to submit an application. The application must exist,
    user must be authenticated and its owner. If its not the case HTTP403 is send

    If validated, application is marked 'submitted' and save with a confirm message

    Args:
        request (HttpRequest): client HTTP reques
        application_id (int): Identifier of the appplicatino to submit

    Returns:
        HttpResponseRedirect: Redirect to application detail page.

    Raises:
        Http404: If no application corresponding to the given id.
        HttpResponseForbidden: If user not the application's owner.
    """
    application = get_object_or_404(Application, id=application_id)

    if application.customer != request.user:
        return HttpResponseForbidden()
    
    application.status = 'submitted'
    application.save()
    
    logger.info(
        'Application %s soumise par %s',
        application.id,
        request.user.username
    )

    messages.add_message(request, messages.INFO, 'Application soumise avec succès')
    return redirect('application-detail')

@login_required
def application_detail(request):
    """
    Displays the detail page of the authenticated user's application.

    This view retrieves the application associated with the currently logged-in
    user and displays its details along with its uploaded documents.

    It also computes the list of required document types that are still missing
    from the application, allowing the user to identify which documents still
    need to be uploaded.

    Args:
        request (HttpRequest): The HTTP request object containing the authenticated user.

    Returns:
        HttpResponse: Renders the 'store/application.html' template with:
            - application: the user's application
            - documents: all documents linked to the application
            - missingDocuments: document types that have not yet been uploaded
    """
    application = get_object_or_404(Application, customer=request.user)
    missing_document_type = DocumentType.objects.exclude(
        id__in=application.documents.values_list('type_id', flat=True)
    )

    return render(request, 'store/application.html', {
        'application': application,
        'documents': application.documents.all(),
        'missingDocuments': missing_document_type
    })

@staff_member_required
def all_applications(request):
    """
    Display all applications.

    Args:
        request (HttpRequest): client HTTP request

    Returns:
        HttpResponse: HTTP Response with template content
        ``store/applications.html`` with applications in context
    """
    applications = Application.objects.filter(status='submitted')
    return render(request, 'store/applications.html', context={"applications": applications})

@login_required
def all_cars(request):
    """
    Display all cars.

    Args:
        request (HttpRequest): client HTTP request

    Returns:
        HttpResponse: HTTP Response with template content
        ``store/allcars.html`` with cars in context
    """
    if not request.user.is_staff:
        logger.warning(
            'Tentative d\'accès à all_cars par %s',
            request.user.username
        )
        raise PermissionDenied()

    cars = Car.objects.all()
    return render(request, 'store/allcars.html', context={"cars": cars})

@login_required
def modify_car(request, car_id):
    """
    Allows a staff user to modify an existing car.

    This view enables the editing of an existing car instance using a form.
    Only authenticated users with staff privileges are allowed to access it.

    The car is retrieved by its ID. On POST requests, the submitted form is
    validated and used to update the existing car instance. On success, a
    confirmation message is displayed and the user is redirected to the same
    modification page.

    On GET requests, the form is pre-filled with the current car data.

    Args:
        request (HttpRequest): The HTTP request object containing user and form data.
        car_id (int): The ID of the car to be modified.

    Returns:
        HttpResponse:
            - Renders 'store/modifycar.html' with the form and car instance.
            - Redirects to 'modify-car' after successful update.

    Raises:
        PermissionDenied: If the user is not a staff member.
        Http404: If no Car matches the given ID.
    """
    if not request.user.is_staff:
        logger.warning(
            'Tentative d\'accès à modify_car par %s',
            request.user.username
        )
        raise PermissionDenied()
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            car = form.save()
            logger.info(
                'Voiture %s modifiée par %s',
                car.id,
                request.user.username
            )
            messages.success(
                request,
                'Informations modifiées avec succès'
            )
            return redirect('modify-car', car_id=car.id)
    else:
        form = CarForm(instance=car)

    return render(request, 'store/modifycar.html', context={"car": car, "form": form})

@login_required
def add_car(request):
    """
    Allows a staff user to add a new car to the system.

    This view handles the creation of a new car instance through a form.
    Only authenticated users with staff privileges are allowed to access it.

    On POST requests, the submitted form is validated and saved if valid.
    A success message is displayed and the user is redirected to the
    'all-cars' page. If the form is invalid, errors are logged.

    On GET requests, an empty form is displayed.

    Args:
        request (HttpRequest): The HTTP request object containing user and form data.

    Returns:
        HttpResponse:
            - Renders 'store/addcar.html' with the form on GET requests or invalid POST.
            - Redirects to 'all-cars' after successful creation.

    Raises:
        PermissionDenied: If the user is not a staff member.
    """
    if not request.user.is_staff:
        logger.warning(
            'Tentative d\'accès à add_car par %s',
            request.user.username
        )
        raise PermissionDenied()

    if request.method == "POST":
        form = CarForm(request.POST)

        if form.is_valid():
            car = form.save()
            logger.info(
                'Voiture %s (%s %s) ajoutée par %s',
                car.id,
                car.brand,
                car.model,
                request.user.username
            )
            messages.success(
                request,
                'Voiture ajoutée avec succès'
            )
            return redirect('all-cars')
        else:
            logger.error('Form invalide: %s', form.errors)

    else:
        form = CarForm()

    return render(request, 'store/addcar.html', {"form": form})

@login_required
def admin_application_detail(request, application_id):
    """
    Displays the detailed view of an application for staff review.

    This view is restricted to staff users only. It retrieves a specific
    application along with all associated documents and renders a review page.

    If a non-staff user attempts to access this view, a warning is logged and
    a PermissionDenied exception is raised.

    Args:
        request (HttpRequest): The HTTP request object containing the user.
        application_id (int): The ID of the application to be reviewed.

    Returns:
        HttpResponse: Renders the 'store/review.html' template with:
            - application: the selected application
            - documents: all documents linked to the application

    Raises:
        PermissionDenied: If the user is not a staff member.
        Http404: If no Application matches the given ID.
    """
    if not request.user.is_staff:
        logger.warning(
            'Tentative d\'accès à admin_application_detail par %s',
            request.user.username
        )
        raise PermissionDenied()

    application = get_object_or_404(Application, id=application_id)
    documents = application.documents.all()
    return render(
        request,
        'store/review.html',
        {'application': application, 'documents': documents}
    )

@login_required
def approve_application(request, application_id):
    """
    Approves a submitted application (staff-only action).

    This view allows a staff member to approve an application that has been
    previously submitted. It enforces strict access control: only users with
    staff privileges can access this endpoint.

    The application must be in the 'submitted' state to be eligible for approval.
    If it is not, the request is rejected with an HTTP 403 response.
    Once approved, the application's status is updated, and the action is logged.
    The view then renders a list of all applications.

    Args:
        request (HttpRequest): The HTTP request object containing the user.
        application_id (int): The ID of the application to approve.

    Returns:
        HttpResponse:
            Renders 'store/applications.html' with the full list of applications
            after successful approval.

    Raises:
        Http404: If no Application matches the given ID.
        PermissionDenied: If the user is not a staff member.
        HttpResponseForbidden: If the application is not in 'submitted' status.
    """
    if not request.user.is_staff:
        logger.warning(
            'Tentative d\'accès à approve_application par %s',
            request.user.username
        )
        raise PermissionDenied()

    application = get_object_or_404(Application, id=application_id)

    if application.status != 'submitted':
        return HttpResponseForbidden("Dossier non soumis")

    application.approve()
    logger.info(
        'Application %s approuvée par %s',
        application.id,
        request.user.username
    )

    applications = Application.objects.all()
    return render(request, 'store/applications.html', context={"applications": applications})

@login_required
def reject_application(request, application_id):
    """
    Rejects a submitted application (staff-only action).

    This view allows a staff member to approve an application that has been
    previously submitted. It enforces strict access control: only users with
    staff privileges can access this endpoint.

    The application must be in the 'submitted' state to be eligible for approval.
    If it is not, the request is rejected with an HTTP 403 response.
    Once rejected, the application's status is updated, and the action is logged.
    The view then renders a list of all applications.

    Args:
        request (HttpRequest): The HTTP request object containing the user.
        application_id (int): The ID of the application to reject.

    Returns:
        HttpResponse:
            Renders 'store/applications.html' with the full list of applications
            after rejection.

    Raises:
        Http404: If no Application matches the given ID.
        PermissionDenied: If the user is not a staff member.
        HttpResponseForbidden: If the application is not in 'submitted' status.
    """
    if not request.user.is_staff:
        logger.warning(
            'Tentative d\'accès à reject_application par %s',
            request.user.username
        )
        raise PermissionDenied()

    application = get_object_or_404(Application, id=application_id)

    if application.status != 'submitted':
        return HttpResponseForbidden("Dossier non soumis")

    application.reject()
    
    logger.info(
        'Application %s rejetée par %s',
        application.id,
        request.user.username
    )

    applications = Application.objects.all()
    return render(request, 'store/applications.html', context={"applications": applications})

@login_required
def view_document(request, document_id):
    """
    Retrieves and serves a document file to an authorized user.

    This view allows an authenticated user to access a document file associated
    with an application. Access is restricted: only the owner of the application
    or a staff member is allowed to view the document.

    If the user is not authorized, a warning is logged and an HTTP 403 response
    is returned.

    The file is served inline (not as an attachment), allowing it to be viewed
    directly in the browser.

    Args:
        request (HttpRequest): The HTTP request object containing the user.
        document_id (int): The ID of the document to retrieve.

    Returns:
        FileResponse:
            Streams the document file content to the client if access is granted.

    Raises:
        Http404: If no Document matches the given ID.
        HttpResponseForbidden: If the user is not the owner of the application
            and is not a staff member.
    """
    doc = get_object_or_404(Document, id=document_id)

    if doc.application.customer != request.user and not request.user.is_staff:
        logger.warning(
            'Tentative d\'accès à view_document par %s',
            request.user.username
        )
        return HttpResponseForbidden()

    return FileResponse(doc.file.open('rb'), as_attachment=False)
