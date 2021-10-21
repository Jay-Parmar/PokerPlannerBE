from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.deletion import CASCADE

from apps.group import models as group_models
from apps.user import models as user_models
from libs import models as util_models

from libs import models as util_models

class Pokerboard(util_models.CommonInfo, util_models.SoftDeletionModel):
    """
    Pokerboard settings model.
    """
    SERIES = 1
    EVEN = 2
    ODD = 3
    FIBONACCI = 4
    CUSTOM = 5
    ESTIMATION_CHOICES = (
        (SERIES, "Series"),
        (EVEN, "Even"),
        (ODD, "Odd"),
        (FIBONACCI, "Fibonacci"),
        (CUSTOM, "Custom"),
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='Creator of Pokerboard'
    )
    estimate_type = models.PositiveSmallIntegerField(
        choices=ESTIMATION_CHOICES, help_text='Estimation type', default=SERIES
    )
    title = models.CharField(unique=True, max_length=20, help_text='Name of Pokerboard')
    description = models.CharField(max_length=100, help_text='Description', null=True, blank=True)
    timer = models.PositiveIntegerField(help_text='Duration for voting (in seconds)',null=True)
    estimation_cards = ArrayField(
        models.PositiveIntegerField(), help_text="Array of estimation values choosed by user",
        null=True
    )

    def __str__(self):
        return self.title


class Invite(util_models.CommonInfo):
    """
    Invites gone to user or group via pokerboard.
    """
    ACCEPTED = 1
    PENDING = 0
    DECLINED = 2
    STATUS_CHOICES = (
        (ACCEPTED,'Accepted'),
        (PENDING,'Pending'),
        (DECLINED,'Declined')
    )
    email = models.EmailField(help_text="Non existing user email", null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, help_text="Person invited", related_name="invites", 
        on_delete=models.CASCADE, null=True, blank=True
    )
    group = models.ForeignKey(
        group_models.Group, help_text="Group Invited", on_delete=models.CASCADE, null=True, blank=True
    )
    pokerboard = models.ForeignKey(
        Pokerboard, help_text="Pokerboard", related_name="invites", on_delete=models.CASCADE
    )
    status = models.PositiveSmallIntegerField(
        help_text="Indicates if invitation accepted or not",choices=STATUS_CHOICES, default=PENDING
    )

    def __str__(self):
        return f'Pokerboard: {self.pokerboard} - Group: {self.group} - User: {self.user}'


class Ticket(util_models.CommonInfo, util_models.SoftDeletionModel):
    """
    Ticket details class.
    """
    UNTOUCHED = 1
    ONGOING = 2
    ESTIMATED = 3
    SKIPPED = 4
    STATUS_CHOICES = (
        (UNTOUCHED, "Untouched"),
        (ONGOING, "Ongoing"),
        (ESTIMATED, "Estimated"),
        (SKIPPED, "Skipped"),
    )

    pokerboard = models.ForeignKey(
        Pokerboard, related_name="tickets", on_delete=models.DO_NOTHING, help_text="Pokerboard to which ticket belongs"
    )
    ticket_id = models.SlugField(help_text="Ticket ID imported from JIRA")
    estimate = models.PositiveIntegerField(null=True, help_text="Final estimate of ticket")
    order = models.PositiveIntegerField(help_text="Order of displaying of tickets")
    status = models.PositiveSmallIntegerField(help_text="Status of ticket", choices=STATUS_CHOICES, default=UNTOUCHED)
    start_datetime = models.DateTimeField(null=True)
    end_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.ticket_id} - {self.pokerboard}'


class UserTicketEstimate(util_models.CommonInfo, util_models.SoftDeletionModel):
    """
    Estimation of ticket by each user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, help_text="Person estimated", related_name="estimations", on_delete=models.CASCADE
    )
    ticket_id = models.ForeignKey(
        Ticket, help_text="Ticket ID on database", related_name="estimations", on_delete=models.CASCADE
    )
    estimate = models.PositiveIntegerField(help_text="Final estimate of ticket")
    estimation_time = models.PositiveIntegerField(help_text="Time taken by user to estimate (in seconds)")

    def __str__(self):
        return f'User {self.user} - Estimated {self.estimate}'


class PokerboardUser(util_models.CommonInfo, util_models.SoftDeletionModel):
    """
    Through table of pokerboard with user.
    """
    SPECTATOR = 1
    CONTRIBUTOR = 2
    ROLE = (
        (SPECTATOR, "Spectator"),
        (CONTRIBUTOR, "Contributor"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, help_text="Users Associated", related_name="pokerboards", on_delete=models.CASCADE
    )
    pokerboard = models.ForeignKey(Pokerboard, help_text="Pokerboards Associated", on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE, help_text="Role", default=CONTRIBUTOR)

    def __str__(self):
        return f'User: {self.user} Role: {self.role} Board: {self.pokerboard}'


class PokerboardGroup(util_models.CommonInfo, util_models.SoftDeletionModel):
    """
    Through table of pokerboard with group.
    """
    SPECTATOR = 1
    CONTRIBUTOR = 2
    ROLE = (
        (SPECTATOR, "Spectator"),
        (CONTRIBUTOR, "Contributor"),
    )
    group = models.ForeignKey(group_models.Group, help_text="Groups Associated", on_delete=models.CASCADE)
    pokerboard = models.ForeignKey(Pokerboard, help_text="Pokerboards Associated", on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE, help_text="Role", default=CONTRIBUTOR)

    def __str__(self):
        return f'Group: {self.group} Role: {self.role} Board: {self.pokerboard}'


class ManagerCredentials(util_models.CommonInfo):
    user = models.OneToOneField(user_models.User, help_text="Manager's details", on_delete=models.CASCADE)
    username = models.EmailField(help_text="Jira Username")
    password = models.CharField(max_length=250, help_text="Jira Password or Token")
    url = models.URLField(help_text="User's Jira Url")

    def __str__(self):
        return f'Manager: {self.user}'
