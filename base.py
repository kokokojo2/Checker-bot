import inspect
from exceptions import ImproperlyConfigured


class BaseFunctionSet:
    silence = {}


class Checker:
    def __init__(self, function_set: BaseFunctionSet):
        if not isinstance(function_set, BaseFunctionSet):
            raise ImproperlyConfigured(f'Checker`s __init__ method expects BaseFunctionSet instance, but'
                                       f' {type(function_set).__name__} was given instead.')

        raw_members = dir(function_set)
        filtered_members = [getattr(function_set, member_name) for member_name in raw_members
                            if member_name.startswith('check_')]
        self.methods = [member for member in filtered_members if inspect.ismethod(member)]
        self.function_set = function_set

        if len(self.methods) == 0:
            raise ImproperlyConfigured(f'Your function_set object does not have any check methods.')

    def run_all_checks(self):
        for method in self.methods:
            code, message, callback_data = method()

            if code == 0:  # means check was successful but did not find something useful
                if method.__name__ not in self.function_set.silence:
                    pass  # TODO: call a bot or email client

            if code == 1:  # means check was successful and found something it is meant to find
                pass  # TODO: call a bot or email client

            if code == -1:  # means there is an error during the check not on the developer side
                pass  # TODO: call a bot or email client

            callback_obj = getattr(
                self.function_set,
                next(filter(lambda x: x.startswith(f'callback_{method.__name__}'), dir(self.function_set)))
                )

            if inspect.ismethod(callback_obj):
                callback_obj(callback_data)
