import inspect
from time import sleep
from exceptions import ImproperlyConfigured


class BaseFunctionSet:
    silenced_checkers = ()  # if the checker is silenced, its messenger is not called on completed check (code 1)
    silent_checkers = ()  # do not require messenger to run successfully

class Checker:
    def __init__(self, function_set: BaseFunctionSet):
        if not isinstance(function_set, BaseFunctionSet):
            raise ImproperlyConfigured(f'Checker`s __init__ method expects BaseFunctionSet instance, but'
                                       f' {type(function_set).__name__} was given instead.')

        raw_members = dir(function_set)
        filtered_checkers = [getattr(function_set, member_name) for member_name in raw_members
                             if member_name.startswith('check_')]
        self.check_methods = [member for member in filtered_checkers if inspect.ismethod(member)]

        filtered_messengers = [getattr(function_set, member_name) for member_name in raw_members
                               if member_name.startswith('message_')]
        self.message_methods = [member for member in filtered_messengers if inspect.ismethod(member)]
        self.function_set = function_set

        # TODO: add check for the presence of messengers

        if len(self.check_methods) == 0:
            raise ImproperlyConfigured(f'Your function_set object does not have any check methods.')

        if len(self.message_methods) == 0:
            raise ImproperlyConfigured(f'Your function_set object does not have any message methods.')

    def __get_method(self, name):
        try:
            method = getattr(
                self.function_set,
                next(filter(lambda x: x.startswith(name), dir(self.function_set)))
            )
        except AttributeError:
            return None

        if inspect.ismethod(method):
            return method

    def run_all_checks(self):
        for method in self.check_methods:
            code, message_context, callback_data = method()

            if method.__name__ not in self.function_set.silent_checkers:
                messenger = self.__get_method(f'message_{method.__name__[6:]}')

                if any(code == status for status in [SUCCESS, ERROR]) or \
                        (method.__name__ not in self.function_set.silenced_checkers and code == COMPLETED):
                    messenger(code, message_context)

            callback_obj = self.__get_method(f'callback_{method.__name__[6:]}')
            if callback_obj is not None:
                callback_obj(code, callback_data)

    def run(self, sleep_time):
        while True:
            self.run_all_checks()
            sleep(sleep_time * 300)
