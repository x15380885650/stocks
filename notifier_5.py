from notifier import Notifier


class FifthNotifier(Notifier):
    def __init__(self):
        super(FifthNotifier, self).__init__(key_prefix='monitor_5')


if __name__ == '__main__':
    notifier = FifthNotifier()
    notifier.run()

