from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, email,  phone_number, username, password, first_name, last_name):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=username,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.is_active = False  # require OTP verification
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username,phone_number,password, first_name, last_name):
        user = self.create_user(
            email,
            username,
            phone_number,
            first_name,
            last_name,
            password
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.role = 'admin'

        user.save(using=self._db)
        return user