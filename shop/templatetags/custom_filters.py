from django import template
from datetime import datetime, timedelta

register = template.Library()

# ✅ Renommage pour éviter conflit avec la fonction abs native
@register.filter(name='absolute')
def absolute(value):
    try:
        return abs(float(value))
    except (TypeError, ValueError):
        return value

@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (TypeError, ValueError):
        return ''

# ✅ Ajout du filtre pour traduire les mois
MOIS = {
    '01': 'JANVIER',
    '02': 'FÉVRIER',
    '03': 'MARS',
    '04': 'AVRIL',
    '05': 'MAI',
    '06': 'JUIN',
    '07': 'JUILLET',
    '08': 'AOÛT',
    '09': 'SEPTEMBRE',
    '10': 'OCTOBRE',
    '11': 'NOVEMBRE',
    '12': 'DÉCEMBRE',
}

@register.filter
def mois_fr(value):
    """
    Retourne le nom du mois en français à partir d'un string comme '01' ou '2024-01'.
    """
    try:
        month_str = str(value)[-2:]  # Prend les 2 derniers caractères
        return MOIS.get(month_str, value)
    except Exception:
        return value

# ✅ Nouveau tag pour faire : {% heure_plus 60 "%H:%M" %}
@register.simple_tag
def heure_plus(minutes=0, fmt="%H:%M"):
    try:
        return (datetime.now() + timedelta(minutes=int(minutes))).strftime(fmt)
    except Exception:
        return datetime.now().strftime(fmt)
@register.filter
def active_si(value, arg):
    """
    Retourne 'active' si value == arg, sinon une chaîne vide.
    """
    try:
        return 'active' if value == arg else ''
    except Exception:
        return ''
# ✅ Filtre pour appliquer la classe 'active' selon une condition
@register.filter
def active_si(value, arg):
    """
    Retourne 'active' si value == arg, sinon une chaîne vide.
    """
    try:
        return 'active' if value == arg else ''
    except Exception:
        return ''
    
@register.filter
def format_prix(value):
    """
    Formate un prix avec des espaces tous les 3 chiffres pour améliorer la lisibilité.
    Exemple : 2000000 → '2 000 000'
    """
    try:
        return f"{int(float(value)):,}".replace(",", " ")
    except (ValueError, TypeError):
        return value
