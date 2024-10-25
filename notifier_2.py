from notifier import Notifier


class SecondNotifier(Notifier):
    def __init__(self):
        super(SecondNotifier, self).__init__(key_prefix='monitor_2')
        self.is_trade_time_forbidden = False


if __name__ == '__main__':
    notifier = SecondNotifier()
    notifier.run()

