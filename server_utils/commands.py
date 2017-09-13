"""
This module is used by the server
It contains the commands utility
"""
import re

PREFIX = '?'


class Command(object):
    """
    This class allows the utilization of commands on a server
    It is used for instantiating, both explicitly and with decorators, storing and detecting commands
    """
    commands = []

    def __init__(self, pattern, name, func, admin_only):
        """
        The class constructor
        :param pattern: python regex pattern
        :param name: name of the command
        :param func: the function of the command
        :param admin_only: whether the command is available for admin users only
        """
        self.name = name
        self.pattern = re.compile(pattern)
        self.admin_only = admin_only
        self.func = func

    def __call__(self, args_obj):
        """
        Makes it so when a command object is called, it calls it's function
        :param args_obj: a command arguments object
        """
        self.func(args_obj)

    @classmethod
    def command(cls, pattern, name=None, admin_only=False):
        """
        The wrapper for the inner function, which adds a command
        :param pattern: python regex pattern
        :param name: name of the command (the function's name by default)
        :param admin_only: whether the command is available for admin users only
        :return: the command's function as received by the inner function
        """
        def inner(func):
            """
            The inner function of the wrapper
            Used to pass the function of the command for the purpose of adding the command itself
            :param func: the command's function
            :return: func (the command's function argument)
            """
            cls.commands.append(cls(pattern, name if name else func.__name__, func, admin_only))
            return func
        return inner

    @classmethod
    def parse_msg(cls, msg):
        """
        Parses a string to determine whether it's command
        :param msg: message string
        :return: the command object if it's a command, otherwise None
        """
        if msg.startswith(PREFIX):
            msg = msg[1:]
            for command in cls.commands:
                if command.pattern.match(msg):
                    return command
        return None


class CommandArgs(object):
    """
    This class is used to pass arguments to command functions
    """
    def __init__(self, server, user, message):
        """
        The class constructor
        :param server: the server which runs the command
        :param user: the User object of sender of the message
        :param message: message string
        """
        self.server = server
        self.user = user
        self.message = message
        self.args = message.split()

    def get_user(self, name):
        """
        Finds a user on the server by their name
        :param name: the requested user's name
        :return: User object if the user was found, otherwise sends the server's
        user-not-found message to the sender of the message
        """
        target = self.server.users_by_nick.get(name)
        if not target:
            self.server.direct_message(self.user, self.server.user_not_found.format(name))
        return target

    @property
    def target(self):
        """
        Gets the User object of the user who were targeted in the command
        :return: User object of the sender of the message if the command is not targeted,
        or target user's User object if they were found, otherwise None
        """
        if len(self.args) <= 1:
            return self.user
        return self.get_user(self.args[1])


@Command.command('^(quit)$')
def quit(args_obj):
    """
    Disconnects a user from the server
    """
    server = args_obj.server
    user = args_obj.user
    server.disconnect_user(user)
    server.broadcast(server.disconnect_message.format(user.display_name))


@Command.command('^(view_commands)$')
def view_commands(args_obj):
    """
    Sends the user a list the commands they are allowed to use
    """
    server = args_obj.server
    user = args_obj.user
    cmds = ', '.join((cmd.name for cmd in Command.commands if not cmd.admin_only or user.is_admin))
    server.direct_message(user, server.commands_message.format(cmds))


@Command.command('^(view_admins)$')
def view_admins(args_obj):
    """
    Sends the user a list of admins in the server
    """
    server = args_obj.server
    admins = ', '.join(nick for nick, user in server.users_by_nick.iteritems() if user.is_admin)
    server.direct_message(args_obj.user, server.admins_message.format(admins))


@Command.command('^(whisper)\s@?\w+\s.+')
def whisper(args_obj):
    """
    Whisper a message in direct_message format to a user
    """
    server = args_obj.server
    user = args_obj.user
    target = args_obj.target
    if not target:
        server.direct_message(user, server.user_not_found.format(target))
        return
    content = ' '.join(args_obj.args[2:])
    server.direct_message(target, server.whisper_message.format(user.display_name, content))


@Command.command('^(kick)\s@?\w+$', admin_only=True)
def kick_user(args_obj):
    """
    Kicks the user from the server
    """
    server = args_obj.server
    user = args_obj.user
    target = args_obj.target
    if not target:
        server.direct_message(user, server.user_not_found.format(target))
        return
    server.direct_message(target, server.kick_message_whisper)
    server.disconnect_user(target)
    server.broadcast(server.kick_message_all.format(target.nickname))


@Command.command('^(mute)\s@?\w+$', admin_only=True)
def mute_user(args_obj):
    """
    Mutes the user
    """
    server = args_obj.server
    user = args_obj.user
    target = args_obj.target
    if not target:
        server.direct_message(user, server.user_not_found.format(target))
        return
    target.muted = True
    server.direct_message(target, server.mute_message)


@Command.command('^(unmute)\s@?\w+$', admin_only=True)
def unmute_user(args_obj):
    """
    Unmutes the user
    """
    server = args_obj.server
    user = args_obj.user
    target = args_obj.target
    if not target:
        server.direct_message(user, server.user_not_found.format(target))
        return
    if target.muted:
        target.muted = False
        server.direct_message(target, server.unmute_message)


@Command.command('^(promote)\s@?\w+$', admin_only=True)
def promote_user(args_obj):
    """
    Promotes a user to admin
    """
    server = args_obj.server
    user = args_obj.user
    target = args_obj.target
    if not target:
        server.direct_message(user, server.user_not_found.format(target))
        return
    if not target.is_admin:
        target.is_admin = True
        server.change_display_name(target, '@' + target.display_name)
        server.direct_message(target, server.promote_message)


@Command.command('^(demote)\s@?\w+$', admin_only=True)
def demote_user(args_obj):
    """
    Demotes the user to regular
    """
    server = args_obj.server
    user = args_obj.user
    target = args_obj.target
    if not target:
        server.direct_message(user, server.user_not_found.format(target))
        return
    if target.is_admin:
        server.change_display_name(target, target.display_name[1:])
        target.is_admin = False
        server.direct_message(target, server.demote_message)


@Command.command('^send_file\s\w+.txt$', admin_only=True)
def send_file(args_obj):
    """
    Downloads a file.
    """
    name = args_obj.args[1]
    server = args_obj.server
    request = server.build_protocol(flags=[server.request_flag, server.file_flag], path=name)
    server.direct_message(args_obj.user, request)
