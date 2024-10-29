from notifier import Notifier


class SixthNotifier(Notifier):
    def __init__(self):
        super(SixthNotifier, self).__init__(key_prefix='monitor_6')
        self.is_trade_time_forbidden = False


if __name__ == '__main__':
    notifier = SixthNotifier()
    notifier.run()

