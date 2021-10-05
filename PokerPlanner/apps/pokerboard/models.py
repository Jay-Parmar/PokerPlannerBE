from django.conf import settings
from django.db import models
from apps.user.models import CommonInfo
from apps.group.models import Group

class Pokerboard(CommonInfo):
    """
    Pokerboard settings model.
    """
    SERIES = 1
    EVEN = 2
    ODD = 3
    FIBONACCI = 4
    ESTIMATION_CHOICES = (
        (SERIES, "Series"),
        (EVEN, "Even"),
        (ODD, "Odd"),
        (FIBONACCI, "Fibonacci"),
    )

    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text='Creator of Pokerboard')
    estimate_type = models.PositiveSmallIntegerField(
        choices=ESTIMATION_CHOICES, help_text='Estimation type', default=SERIES
    )
    title = models.CharField(unique=True, max_length=20, help_text='Name of Pokerboard')
    description = models.CharField(max_length=100, help_text='Description')
    timer = models.PositiveIntegerField(help_text='Duration for voting (in seconds)')
    range_start = models.PositiveIntegerField(help_text="Estimation card range beginning", default=1)
    range_end = models.PositiveIntegerField(help_text="Estimation card range ending", default=10)

    def __str__(self):
        return self.title


class Invites(models.Model):
    """
    Invites gone to user or group via pokerboard.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, help_text="Person invited", related_name="invite", on_delete=models.CASCADE, null=True
    )
    group = models.ForeignKey(Group, help_text="Group Invited", on_delete=models.CASCADE, null=True)
    pokerboard = models.ForeignKey(
        Pokerboard, help_text="Pokerboard", related_name="invites", on_delete=models.CASCADE
    )
    is_accepted = models.BooleanField(default=False, help_text="Indicates if invitation accepted or not")

    def __str__(self):
        return f'Pokerboard: {self.pokerboard} - Group: {self.group} - User: {self.user}'


class Ticket(models.Model):
    """
    Ticket details class
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
        Pokerboard, related_name="tickets", on_delete=models.CASCADE, help_text="Pokerboard to which ticket belongs"
    )
    ticket_id = models.SlugField(help_text="Ticket ID imported from JIRA")
    estimate = models.PositiveIntegerField(null=True, help_text="Final estimate of ticket")
    order = models.PositiveIntegerField(help_text="Order of display of tickets")
    status = models.PositiveSmallIntegerField(help_text="Status of ticket", choices=STATUS_CHOICES, default=UNTOUCHED)
    start_datetime = models.DateTimeField(null=True)
    end_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.ticket_id} - {self.pokerboard}'


class UserTicketEstimate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, help_text="Person estimated", 
        related_name="estimations", on_delete=models.DO_NOTHING, null=False
    )
    ticket_id = models.ForeignKey(
        Ticket, help_text="Ticket ID on database", null=False, related_name="estimations", on_delete=models.DO_NOTHING
    )
    estimate = models.PositiveIntegerField(null=False, help_text="Final estimate of ticket")
    estimation_time = models.PositiveIntegerField(
        null=False, help_text="Time taken by user to estimate (in seconds)"
    )

    def __str__(self):
        return f'User {self.user} - Estimated {self.estimate}'


class PokerboardUser(models.Model):
    SPECTATOR = 1
    CONTRIBUTOR = 2
    ROLE = (
        (SPECTATOR, "Spectator"),
        (CONTRIBUTOR, "Contributor"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, help_text="Users Associated", related_name="pokerboards", on_delete=models.CASCADE, null=False
    )
    pokerboard = models.ForeignKey(
        Pokerboard, help_text="Pokerboards Associated", on_delete=models.CASCADE
    )
    role = models.PositiveSmallIntegerField(choices=ROLE, help_text="Role", default=CONTRIBUTOR)


class PokerboardGroup(models.Model):
    SPECTATOR = 1
    CONTRIBUTOR = 2
    ROLE = (
        (SPECTATOR, "Spectator"),
        (CONTRIBUTOR, "Contributor"),
    )
    group = models.ForeignKey(Group, help_text="Groups Associated", on_delete=models.CASCADE, null=False)
    pokerboard = models.ForeignKey(
        Pokerboard, help_text="Pokerboards Associated", on_delete=models.CASCADE
    )
    role = models.PositiveSmallIntegerField(choices=ROLE, help_text="Role", default=CONTRIBUTOR)
