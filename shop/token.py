from django.contrib.auth.tokens import PasswordResetTokenGenerator
# Vous pouvez ne plus avoir besoin de 'six' pour Python 3
# from six import text_type

class Token_generator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):  
        # Assurez-vous que vous combinez correctement les données et que vous les convertissez en chaîne
        return str(user.pk) + str(timestamp)  # Concaténez les valeurs en chaîne de caractères

# Créez une instance de votre générateur de token

generator_token = Token_generator()
