from django.db import models

class Menu(models.Model):
    name = models.CharField(max_length=100)

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=500)
    url = models.CharField(max_length=100)
    login_required = models.BooleanField(blank=True, default=False)
    staff_required = models.BooleanField(blank=True, default=False)
    menu = models.ForeignKey(Menu)

class Setting(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField(null=True, blank=True)

class Group(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    members = models.ManyToManyField('Key', through='KeyGroup', blank=True)

class Host(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    task_id = models.CharField(max_length=36, null=True, blank=True)
    status = models.CharField(max_length=10, null=True, blank=True)

class Osuser(models.Model):
    name = models.CharField(max_length=200, unique=True)
    home = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)

KEYTYPE_CHOICES = (
    ('ssh-rsa', 'ssh-rsa'),
    ('ssh-dsa', 'ssh-dsa'),
)

class Key(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    firstname = models.CharField(max_length=200, null=True, blank=True)
    lastname = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    keytype = models.CharField(max_length=10, null=True, choices=KEYTYPE_CHOICES, default='RSA',)
    publickey = models.TextField(null=True, blank=True)
    member_of = models.ManyToManyField('Group', through='KeyGroup', blank=True)

class KeyGroup(models.Model):
    key = models.ForeignKey('Key', on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)

class Permission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    osuser = models.ForeignKey(Osuser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("group", "host", "osuser")
