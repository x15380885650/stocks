from notifier import Notifier


class FourthNotifier(Notifier):
    def __init__(self):
        super(FourthNotifier, self).__init__(key_prefix='monitor_4')
        self.is_trade_time_forbidden = False


if __name__ == '__main__':
    notifier = FourthNotifier()
    notifier.run()

