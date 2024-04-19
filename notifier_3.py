from notifier import Notifier


class ThirdNotifier(Notifier):
    def __init__(self):
        super(ThirdNotifier, self).__init__(key_prefix='monitor_3')


if __name__ == '__main__':
    notifier = ThirdNotifier()
    notifier.run()

