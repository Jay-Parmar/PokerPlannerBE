from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from apps.user import models as user_models


class UserTests(APITestCase):

    def setUp(self):
        self.user = {
            "user": {
                "first_name": "setup",
                "last_name": "user",
                "email": "setupuser@gmail.com",
                "password": "setupuser@gmail.com",
            }
        }
        self.response = self.client.post(reverse('user-list'), self.user, format='json')

    def test_can_create_user(self):
        """
        Ensure we can create a new user object.
        """
        data = {
            "user": {
                "email": "somename@gmail.com",
                "first_name": "some",
                "last_name": "name",
                "password": "somename@gmail.com",
            }
        }
        response = self.client.post(reverse('user-list'), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = user_models.User.objects.filter(email=data["user"]["email"]).first()
        self.assertIsNotNone(user)
        self.assertEqual(user_models.User.objects.count(), 2)
        expected_data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "token": Token.objects.get(user=user).key
        }
        self.assertEqual(response.data, expected_data)

    def test_create_existing_user(self):
        """
        Ensure we cannot create a new user object whose email is already present.
        """
        data = {
            "user": {
                "email": "setupuser@gmail.com",
                "first_name": "some",
                "last_name": "name",
                "password": "somename@gmail.com",
            }
        }
        response = self.client.post(reverse('user-list'), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_data = {
            'email': [
                'user with this email already exists.'
            ]
        }
        self.assertEqual(response.data, expected_data)

    def test_create_user_without_first_name(self):
        """
        Ensure the User model won't be created for bad data.
        """
        bad_data = {
            "user": {
                            "email": "somename@gmail.com",
                "last_name": "name",
                "password": "somename@gmail.com",
            }
        }
        expected_data = {
            "first_name": [
                "This field is required."
            ]
        }
        response = self.client.post(reverse('user-list'), data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_create_user_without_email(self):
        """
        Ensure the User model won't be created for bad data.
        """
        bad_data = {
            "user": {
                "first_name": "some",
                "last_name": "name",
                "password": "somename@gmail.com",
            }
        }
        expected_data = {
            "email": [
                "This field is required."
            ]
        }
        response = self.client.post(reverse('user-list'), data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_create_user_with_invalid_email(self):
        """
        Ensure the user isn't created with invalid email.
        """
        bad_data = {
            "user": {
                "first_name": "some",
                "email": "email",
                "last_name": "name",
                "password": "somename@gmail.com",
            }
        }
        expected_data = {
            "email": [
                "Enter a valid email address."
            ]
        }
        response = self.client.post(reverse('user-list'), data=bad_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(expected_data, response.data)

    def test_create_user_without_password(self):
        """
        Ensure user won't be created without password.
        """
        bad_data = {
            "user": {
                "first_name": "some",
                "last_name": "user",
                "email": "someuser@gmail.com",
            }
        }
        expected_data = {
            "password": [
                "This field is required."
            ]
        }
        response = self.client.post(reverse('user-list'), data=bad_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(expected_data, response.data)

    def test_update_user_first_name(self):
        """
        Test if user can update first name.
        """
        data = {
            "first_name": "something",
        }
        expected_data = {
            "id": self.response.data["id"],
            "first_name": data["first_name"],
            "last_name": self.user["user"]["last_name"],
            "email": self.user["user"]["email"],
        }
        print("expected ::: ",expected_data)
        url = reverse('user-detail', args=[self.response.data["id"]])
        response = self.client.patch(url, data=data, format="json")
        print("respo ::: ",response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_data, response.data)

    def test_login(self):
        """
        Ensures user can log in using correct creds.
        """
        login_credentials = {
            "user": {
                "email": self.user["user"]["email"],
                "password": self.user["user"]["password"],
            }  
        }
        user = user_models.User.objects.filter(email=self.user["user"]["email"]).first()
        login_response = self.client.post(reverse('login'), login_credentials, format="json")
        expected_data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "token": Token.objects.get(user=user).key,
        }
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(login_response.data, expected_data)

    def test_invalid_password_login(self):
        """
        Ensures user cannot log in using invalid creds.
        """
        login_credentials = {
            "user": {
                "email": self.user["user"]["email"],
                "password": "differentpassword",
            }
        }
        login_response = self.client.post(reverse('login'), login_credentials, format="json")
        expected_data = {
            'non_field_errors': [
                ErrorDetail(string='Invalid Credentials', code='invalid')
            ]
        }
        self.assertEqual(login_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(login_response.data, expected_data)

    def test_invalid_email_login(self):
        """
        Ensures user cannot log in using invalid creds.
        """
        login_credentials = {
            "user": {
                "email": "invalidemail@gmail.com",
                "password": self.user["user"]["password"],
            }
        }
        login_response = self.client.post(reverse('login'), login_credentials, format="json")
        expected_data = {
            'non_field_errors': [
                'Invalid Credentials'
            ]
        }
        self.assertEqual(login_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(login_response.data, expected_data)

    def test_logout(self):
        """
        Ensures user cannot log in using invalid creds.
        """
        login_credentials = {
            "user": {
                "email": "invalidemail@gmail.com",
                "password": self.user["user"]["password"],
            }
        }
        login_response = self.client.post(reverse('login'), login_credentials, format="json")
        expected_data = {
            'non_field_errors': [
                'Invalid Credentials'
            ]
        }
        self.assertEqual(login_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(login_response.data, expected_data)

    def test_can_delete_user(self):
        """
        Ensure user can delete itself.
        """
        id = user_models.User.objects.get().id
        response = self.client.delete(reverse('user-detail', args=[id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deleted_user_also_present(self):
        """
        Ensures the user is not hard deleted but soft deleted.
        """
        id = user_models.User.objects.get().id
        user = user_models.User.objects.get(id=id)
        previous_data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        self.client.delete(reverse('user-detail', args=[id]))
        deleted_user = user_models.User.all_objects.get(id=id)
        deleted_data = {
            "id": deleted_user.id,
            "email": deleted_user.email,
            "first_name": deleted_user.first_name,
            "last_name": deleted_user.last_name,
        }
        self.assertEqual(deleted_data, previous_data)

    def test_deleted_user_restore(self):
        """
        Ensure deleted user can be restored.
        """
        id = user_models.User.objects.get().id
        user = user_models.User.objects.get(id=id)
        previous_data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        response = self.client.delete(reverse('user-detail', args=[id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.restore()
        restored_user = user_models.User.objects.get(id=id)
        restored_data = {
            "id": restored_user.id,
            "email": restored_user.email,
            "first_name": restored_user.first_name,
            "last_name": restored_user.last_name,
        }
        self.assertEqual(restored_data, previous_data)

    def test_create_deleted_user(self):
        """
        Ensures user can create another account if previous accunt was soft deleted.
        """
        id = user_models.User.objects.get().id
        user = user_models.User.objects.get(id=id)
        previous_email = user.email
        previous_data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        self.client.delete(reverse('user-detail', args=[id]))
        new_data = {
            "user": {
                "email": previous_email,
                "first_name": "newName",
                "last_name": "newLastname",
                "password": "password"
            }
        }
        response = self.client.post(reverse('user-list'), new_data, format="json")
        user = user_models.User.objects.filter(email=new_data["user"]["email"]).first()
        expected_data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "token": Token.objects.get(user=user).key
        }
        self.assertEqual(response.data, expected_data)
