from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home_view(request):
    """
    Vista principal a la que se accede tras iniciar sesión.
    Muestra la página de bienvenida con la barra de navegación.
    """
    return render(request, 'home.html', {"titulo": "Inicio - EcoTech Solutions"})