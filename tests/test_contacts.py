from unittest import TestCase

from earful.contacts import (
    EmailAddress,
    PhoneNumber,
    HipChat,
    Recipient,
    Group,
    )


class ContactInformationTest(TestCase):
    def test_hipchat_defaults(self):
        instance = HipChat('contactname', 'roomname')
        self.assertEqual(instance.name, 'contactname')
        self.assertEqual(instance.weight, 100)
        self.assertEqual(instance.room, 'roomname')
        self.assertTrue(instance.notify)
        self.assertFalse(instance.mention)

    def test_hipchat_withuser(self):
        instance = HipChat('contactname', 'roomname', username='person')
        self.assertFalse(instance.notify)
        self.assertTrue(instance.mention)

    def test_hipchat_setprefs(self):
        instance = HipChat('contactname', 'roomname', username='person', notify=True, mention=False)
        self.assertTrue(instance.notify)
        self.assertFalse(instance.mention)


class RecipientTest(TestCase):
    def test_recipient_defaults(self):
        r = Recipient('recipientname')
        self.assertEqual(list(r.contacts()), [])

    def test_simple_recipient(self):
        c = [EmailAddress('emailname', 'emailaddr')]
        r = Recipient('recipientname', contacts=c)
        self.assertEqual(list(r.contacts()), c)

    def test_less_simple_recipient(self):
        c = [
            EmailAddress('emailname', 'emailaddr'),
            PhoneNumber('phonename', 'phonenum'),
        ]
        r = Recipient('recipientname', contacts=c)
        self.assertEqual(list(r.contacts()), c)

    def test_contacts_by_type(self):
        c = [
            EmailAddress('emailname', 'emailaddr'),
            PhoneNumber('phonename', 'phonenum'),
        ]
        r = Recipient('recipientname', contacts=c)
        self.assertEqual(list(r.contacts(of_type=EmailAddress)), [c[0]])

    def test_contacts_with_weight(self):
        c = [
            EmailAddress('emailname', 'emailaddr'),
            EmailAddress('emailname', 'emailaddr', weight=50),
            PhoneNumber('phonename', 'phonenum'),
        ]
        r = Recipient('recipientname', contacts=c)
        self.assertEqual(list(r.contacts()), c[1:])

    def test_contacts_with_weight_all(self):
        c = [
            EmailAddress('emailname', 'emailaddr'),
            EmailAddress('emailname', 'emailaddr', weight=50),
            PhoneNumber('phonename', 'phonenum'),
        ]
        r = Recipient('recipientname', contacts=c)
        self.assertEqual(list(r.contacts(include_all=True)), [c[1], c[0], c[2]])

    def test_contacts_with_weight_type(self):
        c = [
            EmailAddress('emailname', 'emailaddr'),
            EmailAddress('emailname', 'emailaddr', weight=50),
            PhoneNumber('phonename', 'phonenum'),
        ]
        r = Recipient('recipientname', contacts=c)
        self.assertEqual(list(r.contacts(of_type=EmailAddress)), [c[1]])

    def test_contacts_having(self):
        c = [
            PhoneNumber('phonename', 'phonenum', sms_ok=False),
            PhoneNumber('phonename', 'phonenum', sms_ok=True),
        ]
        r = Recipient('recipientname', contacts=c)
        self.assertEqual(list(r.contacts(sms_ok=True)), [c[1]])


class GroupTest(TestCase):
    def test_groups(self):
        t = EmailAddress('emailname', 'emailaddr')
        r = Recipient('recipientname', contacts=[t])
        c = Group('c', recipients=[r])
        b = Group('b', groups=[c])
        a = Group('a', groups=[b])

        self.assertEqual(list(a.groups(recursive=False)), [b])
        self.assertEqual(list(a.recipients(recursive=False)), [])
        self.assertEqual(list(a.contacts(recursive=False)), [])

        self.assertEqual(list(a.groups()), [b, c])
        self.assertEqual(list(a.recipients()), [r])
        self.assertEqual(list(a.contacts()), [t])
