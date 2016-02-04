class ContactInformation(object):
    def __init__(self, name, weight=100, *args, **kwargs):
        self.name = name
        self.weight = weight

    def __str__(self):
        return "Unusable Contact: {:s} ({:d})".format(self.name, self.weight)


class EmailAddress(ContactInformation):
    def __init__(self, email, *args, **kwargs):
        super(EmailAddress, self).__init__(*args, **kwargs)
        self.email = email

    def __str__(self):
        return "Email: {:s} <{:s}> ({:d})".format(self.name, self.email, self.weight)


class PhoneNumber(ContactInformation):
    def __init__(self, phone, sms_ok=True, voice_ok=False, *args, **kwargs):
        super(PhoneNumber, self).__init__(*args, **kwargs)
        self.phone = phone
        self.sms_ok = sms_ok
        self.voice_ok = voice_ok

    def __str__(self):
        methods = []
        if self.sms_ok:
            methods.append('sms')
        if self.voice_ok:
            methods.append('voice')
        return "Phone: {:s} <{:s}> [{:s}] ({:d})".format(self.name, self.phone, ', '.join(methods), self.weight)


class HipChat(ContactInformation):
    def __init__(self, room, username=None, mention=None, notify=None, server=None, *args, **kwargs):
        super(HipChat, self).__init__(*args, **kwargs)
        self.room = room
        self.username = username
        self.server = server

        if mention is None:
            self.mention = True if username else False
        else:
            self.mention = mention

        if notify is None:
            self.notify = False if username else True
        else:
            self.notify = notify

    def __str__(self):
        path = [self.room]
        if self.server:
            path.insert(0, self.server)
        if self.username:
            path.append(self.username)

        features = []
        if self.mention:
            features.append('mention')
        if self.notify:
            features.append('notify')

        return "HipChat: {:s} <{:s}> [{:s}] ({:d})".format(self.name, '/'.join(path), ', '.join(features), self.weight)


class Recipient(object):
    def __init__(self, name, contacts=None, *args, **kwargs):
        self.name = name
        self._contacts = contacts or []

    def __str__(self):
        return "{:s}: {:s}: {:s}".format(self.__class__.__name__, self.name, map(str, self.contacts) or 'No Contact Information')

    def contacts(self, of_type=None, include_all=False, **having):
        returned_types = []
        for contact in sorted(self.contacts, key=lambda v: v.weight):
            if of_type and not isinstance(contact, of_type):
                continue
            for key, value in having.items():
                if getattr(contact, key, None) != value:
                    continue
            if not include_all and contact.__class__ in returned_types:
                continue
            returned_types.append(contact.__class__)
            yield contact


class Group(object):
    def __init__(self, name, groups=None, recipients=None, *args, **kwargs):
        self.name = name
        self._groups = groups or []
        self._recipients recipients or []

    def groups(self, recursive=True):
        for group in self._groups:
            yield group
            if recursive:
                for group_ in group.groups(recursive=True):
                    yield group_

    def recipients(self, recursive=True):
        for recipient in self.recipients:
            yield recipient
        for group in self.groups(recursive=False):
            for recipient in group.recipients(recursive=recursive):
                yield recipient

    def contacts(self, of_type=None, include_all=False, recursive=True, **having):
        for recipient in self.recipients(recursive=recursive):
            for contact in recipient.contacts(of_type=of_type, include_all=include_all, **having):
                yield contact
