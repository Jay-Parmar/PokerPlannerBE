from ddf import G

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.group import models as group_models


class GroupTestCases(APITestCase):
    """
    Group testcases for testing group list, details and add member functionality
    """
    GROUP_URL = reverse('group-list')
    ADD_MEMBER_URL = reverse('add')

    def setUp(self):
        self.user = G(get_user_model())
        token = G(Token, user=self.user)
        self.group = G(group_models.Group, owner=self.user, name="Developers")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_create_group_unique_name(self):
        """
        Creates group, expects 400 response code on non-unique name
        """
        data = {
            "name": self.group.name,
        }
        expected_data = {
            "name": [
                "group with this name already exists."
            ]
        }
        response = self.client.post(self.GROUP_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)

    def test_create_group_failure_empty_name(self):
        """
        Create group, expects bad request on empty group name
        """
        data = {
            "name": ""
        }
        expected_data = {
            "name": [
                "This field may not be blank."
            ]
        }
        response = self.client.post(self.GROUP_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)

    def test_create_group_failure_without_name(self):
        """
        Create group, expects bad request on no group name
        """
        data = {}
        expected_data = {
            "name": [
                "This field is required."
            ]
        }
        response = self.client.post(self.GROUP_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)

    def test_get_group_details_not_found(self):
        """
        Get group details by groupId, Expects 404 on invalid groupId
        """
        response = self.client.get(reverse('group-detail', args=[100]))
        self.assertEqual(response.status_code, 404)

    def test_list_group(self):
        """
        Get group list, checks for group's size
        """
        response = self.client.get(self.GROUP_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_group_details(self):
        """
        Get group details by groupId, Expects 200 response code
        """
        expected_data = {
            "id": self.group.id,
            "name": self.group.name,
            "owner": self.user.id,
            "members": []
        }
        response = self.client.get(reverse('group-detail', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(expected_data, response.data)

    def test_add_user_group(self):
        """
        Add member to group, Expects 201 response code
        """
        data = {
            "email": self.user.email,
            "group": self.group.id
        }
        response = self.client.post(self.ADD_MEMBER_URL, data)
        self.assertEqual(response.status_code, 201)

    def test_add_member_failure_multiple_times(self):
        """
        Add member to group, Expects 400 response code on adding a member two times
        """
        data = {
            "email": self.user.email,
            "group": self.group.id
        }
        expected_data = {
            "non_field_errors": [
                "A member can't be added to a group twice"
            ]
        }
        response = self.client.post(self.ADD_MEMBER_URL, data)
        self.client.post(self.ADD_MEMBER_URL, data)
        response = self.client.post(self.ADD_MEMBER_URL, data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)

    def test_add_member_failure_without_email(self):
        """
        Add member to group, Expects 400 response code on adding a member without email
        """
        data = {
            "group": self.group.id
        }
        expected_data = {
            "email": [
                "This field is required."
            ]
        }
        response = self.client.post(self.ADD_MEMBER_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)

    def test_add_member_failure_without_group(self):
        """
        Add member to group, Expects 400 response code on not providing group
        """
        data = {
            "email": self.user.email
        }
        expected_data = {
            "group": [
                "This field is required."
            ]
        }

        response = self.client.post(self.ADD_MEMBER_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)

    def test_add_member_for_non_existing_member(self):
        """
        Add member to group, Expects 400 response code on providing unregistered email
        """
        data = {
            "group": self.group.id,
            "email": "test@test.com"
        }
        expected_data = {
            "non_field_errors": [
                "No such user"
            ]
        }
        response = self.client.post(self.ADD_MEMBER_URL, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, expected_data)




