from notifier import Notifier


class SecondNotifier(Notifier):
    def __init__(self):
        super(SecondNotifier, self).__init__(key_prefix='monitor_2')


if __name__ == '__main__':
    notifier = SecondNotifier()
    notifier.run()

