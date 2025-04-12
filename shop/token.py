from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
import datetime

class Token_generator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):  
        # Assurez-vous que vous combinez correctement les données et que vous les convertissez en chaîne
        return str(user.pk) + str(timestamp)  # Concaténez les valeurs en chaîne de caractères

    def check_token(self, user, token):
        # Vérification standard de Django
        if not super().check_token(user, token):
            return False

        # Vérification personnalisée : expiration dans 1 jour à partir de created_at
        expiration_time = user.created_at + datetime.timedelta(days=1)
        return timezone.now() <= expiration_time

# Créez une instance de votre générateur de token
generator_token = Token_generator()
