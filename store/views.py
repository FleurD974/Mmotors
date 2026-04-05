from django.shortcuts import get_object_or_404, render

from store.models import Car

def index(request):
    cars = Car.objects.all()

    return render(request, 'store/index.html', context={"cars": cars})

def car_detail(request, slug):
    car = get_object_or_404(Car, slug=slug)
    return render(request, 'store/detail.html', context={"car": car})
