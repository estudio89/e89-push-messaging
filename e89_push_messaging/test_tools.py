# -*- coding: utf-8 -*-
from django.db.models.signals import pre_delete,post_save
from django.conf import settings
import e89_push_messaging.push_tools
import contextlib

@contextlib.contextmanager
def mock_push(Model):
    """
    Mocks temporarily the sending of push messages for test purposes.

    Usage:
        with mock_push(Model) as receiver:
            instance.notify_owners()
            self.assertEqual(receiver.notified, set([instance.owner.id]))
    """

    from signals import notify_owner
    send_on_save = settings.PUSH_MODELS[Model._meta.app_label + "." + Model._meta.object_name].get("send_on_save", True)

    fake_receiver = FakeNotifyOwner()

    pre_delete.disconnect(notify_owner, Model)
    pre_delete.connect(fake_receiver, sender=Model)

    if send_on_save:
        post_save.disconnect(notify_owner, Model)
        post_save.connect(fake_receiver, sender=Model)

    old_method = Model.notify_owners
    mock_method = lambda self: fake_receiver(self._meta.model, self, None)
    Model.notify_owners = mock_method
    yield fake_receiver
    pre_delete.disconnect(fake_receiver, Model)
    pre_delete.connect(notify_owner, sender=Model)

    if send_on_save:
        post_save.disconnect(fake_receiver, Model)
        post_save.connect(notify_owner, sender=Model)
    Model.notify_owners = old_method

class FakeNotifyOwner(object):
    def __init__(self):
        self.notified = set()

    def __call__(self, sender, instance, signal, **kwargs):
        from signals import notify_owner

        result = notify_owner(sender, instance, signal, testing=True)

        if result is None:
            # Push was not sent
            return
        owners, exclude_reg_ids, include_reg_ids = result

        for owner in owners:
            if e89_push_messaging.push_tools.is_id(owner):
                owner_id = owner
            else:
                owner_id = owner.id
            if not owner_id in exclude_reg_ids:
                self.notified.add(owner_id)

        for include in include_reg_ids:
            if e89_push_messaging.push_tools.is_id(include):
                self.notified.add(include)
