from notifier import Notifier


class FirstNotifier(Notifier):
    def __init__(self):
        super(FirstNotifier, self).__init__(key_prefix='monitor_1')


if __name__ == '__main__':
    notifier = FirstNotifier()
    notifier.run()