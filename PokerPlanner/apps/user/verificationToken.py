from django.contrib.auth.tokens import PasswordResetTokenGenerator

class VerifyEmailTokenGenerator(PasswordResetTokenGenerator):
    pass

account_activation_token = VerifyEmailTokenGenerator()
