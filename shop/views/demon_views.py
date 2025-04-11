from django.shortcuts import render

def demo_interactive(request):
    """Affiche la page de démonstration interactive."""
    return render(request, 'demo_interactive.html')