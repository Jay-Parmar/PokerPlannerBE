import json
from ddf import G

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from apps.group.models import Group
from apps.pokerboard.models import Pokerboard, Invite
from apps.user.models import User


class InviteTestCases(APITestCase):
    """
    Test case for invite to pokerboard API
    """
    def setUp(self):
        """
        Function to make Group, User, Token and Pokerboard for all test cases
        """
        self.user1 = G(User, email="manikanand@yahoo.com")
        self.user2 = G(User, email="jay@gmail.com")
        self.user3 = G(User, email="utsav@gmail.com")
        self.token1 = G(Token, user=self.user1)
        self.pokerboard = G(Pokerboard, manager=self.user1, timer="30")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        self.group1 = G(Group, owner=self.user3, name="mygroup")
        self.group1.members.add(self.user3)
        self.group2 = G(Group, owner=self.user2, name="mygroup2")
        self.group2.members.add(self.user2)
        self.group2.members.add(self.user3)
        self.INVITE_URL = reverse('invite-list')

    def invite_user_test(self):
        """
        Inviting User Testcases
        """
        data = {
            "email": self.user2.email,
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)

        expected_data = {
            "pokerboard": self.pokerboard.id,
            "group_id": None,
            "email": self.user2.email
        }
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(expected_data, response.data)

        # Alreaady Invited User Test
        data = {
            "email": self.user2.email,
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = ["Invite already sent!"]
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(expected_data, response.data)

        # Invite Accepting Code
        invite = Invite.objects.get(
            pokerboard_id=self.pokerboard.id, user_id=self.user2)
        self.INVITE_URL_DETAIL = reverse('invite-detail', args=[invite.id])
        token2 = G(Token, user=self.user2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2.key)
        response = self.client.patch(self.INVITE_URL_DETAIL, data={})
        expected_data = ["Added to the pokerboard"]
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(expected_data, response.data)

        # When User already accepted the invite
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = ["Already part of pokerboard"]
        self.assertListEqual(expected_data, response.data)
        self.assertEqual(response.status_code, 400)

        # Test code to delete the invite
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2.key)
        invite = Invite.objects.get(user=self.user2)
        response = self.client.delete(
            reverse('invite-detail', args=[invite.id]))
        expected_data = {"detail": "Not found."}
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(expected_data, response.data)

    def invite_passing_manager_details_test(self):
        """
        Inviting manager again
        """
        data = {
            "pokerboard": self.pokerboard,
            "email": self.user1.email
        }
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = ["Manager cannot be invited!"]
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(expected_data, response.data)
        

    def invite_not_registered_user_test(self):
        """
        Inviting user who has not signed up
        """
        data = {
            "email": "manik.anand@joshtechnologygroup.com",
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = [
            "Email to signup in pokerplanner has been sent.Please check your email."
        ]
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(expected_data, response.data)

    def invite_group_test(self):
        """
        Invite by group id.
        """
        data = {
            "group_id": self.group2.id,
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = {
            "pokerboard": self.pokerboard.id,
            "group_id": self.group2.id,
        }
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(expected_data, response.data)


    def invite_without_passing_emailgroupid_test(self):
        """
        Not passing email and groupid
        """
        data = {"pokerboard": self.pokerboard.id}
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = ["Group id or Email id is missing"]
        self.assertEqual(response.status_code, 400)
        self.assertListEqual(expected_data, response.data)

    def invite_by_user_token_test(self):
        """
        User inviting the members and not manager
        """
        data = {
            "email": self.user2.email,
            "pokerboard": self.pokerboard.id
        }
        token2 = G(Token, user=self.user2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2.key)
        response = self.client.post(self.INVITE_URL, data=data)
        expected_data = {"detail": "You do not have permission to perform this action."}
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(expected_data, response.data)
    
    def invite_without_passing_pokerboard_test(self):
        """
        Invite user without passing email or group id.
        """
        data = {"email": self.user2.email}
        response = self.client.post(self.INVITE_URL, data=json.dumps(
            data), content_type='application/json')
        expected_data = {"pokerboard": ["This field is required."]}
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(expected_data, response.data)

    def delete_invite_test(self):
        """
        Test case to delete invite.
        """
        data = {
            "email": self.user3.email,
            "pokerboard": self.pokerboard.id
        }
        response = self.client.post(self.INVITE_URL, data=data)
        if self.assertEqual(response.status_code, 201):
            invite = Invite.objects.get(email=data['email'], pokerboard=data['pokerboard'])
            response = self.client.delete(reverse('invite-detail', args=[invite.id]))
            expected_data = {"msg": "Invite successfully revoked."}
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual(expected_data, response.data)

    def delete_invite_notexist_test(self):
        """
        Test case to delete invite which does not exist.
        """
        response = self.client.delete(reverse('invite-detail', args=[500]))
        expected_data = {"detail": "Not found."}
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(expected_data, response.data)
