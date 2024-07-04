import os, signal, time, redis, datetime
from redis import StrictRedis

PARENT_PATH = '/home/stocks'


class ScriptManager(object):
    def __init__(self):
        self.scrip_list = [
            {'name': 'monitor_1', 'redis_prefix': 'monitor_1'},
            {'name': 'monitor_2', 'redis_prefix': 'monitor_2'},
            {'name': 'monitor_3', 'redis_prefix': 'monitor_3'},
            {'name': 'monitor_4', 'redis_prefix': 'monitor_4'},
            {'name': 'monitor_5', 'redis_prefix': 'monitor_5'},

            {'name': 'notifier_1', 'redis_prefix': 'monitor_1'},
            {'name': 'notifier_2', 'redis_prefix': 'monitor_2'},
            {'name': 'notifier_3', 'redis_prefix': 'monitor_3'},
            {'name': 'notifier_4', 'redis_prefix': 'monitor_4'},
            {'name': 'notifier_5', 'redis_prefix': 'monitor_5'},
        ]
        self.redis_conf = {'host': '127.0.0.1', 'port': 6408, 'password': 'iscas139', 'db': 0}
        self.redis = StrictRedis(**self.redis_conf, decode_responses=True)

    def get_pid_list_by_name(self, script_name):
        pid_list = []
        grep_str = "ps -ux | grep %s | grep -v grep | awk '{print $2}'" % script_name
        # print(grep_str)
        grep_res = os.popen(grep_str).read()
        if not grep_res:
            return pid_list
        for pid in grep_res.split('\n'):
            if not pid:
                continue
            pid_list.append(pid)
        return pid_list

    def kill_process_by_pid(self, pid):
        print('kill_process_by_pid, pid: {}'.format(pid))
        os.kill(int(pid), signal.SIGKILL)

    def start_process(self, scrip_file_path, log_file_path, script):
        start_cmd = 'nohup python3 -u {} >{} 2>&1 &'.format(scrip_file_path, log_file_path)
        print('start_cmd: {}'.format(start_cmd))
        start_cmd_result = os.system(start_cmd)
        print('start_cmd_result: {}'.format(start_cmd_result))
        self.set_script_start_time(script)

    def get_script_stop_status(self, script):
        key = '{}:is_stop'.format(script['redis_prefix'])
        is_stop = self.redis.get(key)
        if is_stop is None:
            is_stop = 0
            self.redis.set(key, is_stop)
        return int(is_stop)

    def set_script_start_time(self, script):
        key = '{}:{}_start_time'.format(script['redis_prefix'], script['name'])
        now_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        self.redis.set(key, now_time)

    def get_script_start_time(self, script):
        key = '{}:{}_start_time'.format(script['redis_prefix'], script['name'])
        return self.redis.get(key)

    def kill_process_by_id_list(self, pid_list):
        for p_id in pid_list:
            self.kill_process_by_pid(p_id)

    def run(self):
        logs_path = '{}/logs'.format(PARENT_PATH)
        for script in self.scrip_list:
            scrip_name = script['name']
            py_name = '{}.py'.format(scrip_name)
            pid_list = self.get_pid_list_by_name(py_name)
            print('py_name: {}, {} scripts is running...'.format(py_name, len(pid_list)))
            is_stop = self.get_script_stop_status(script)
            scrip_file_path = '{}/{}'.format(PARENT_PATH, py_name)
            log_file_path = '{}/{}.log'.format(logs_path, scrip_name)
            if len(pid_list) == 1 and not is_stop:
                script_start_time = self.get_script_start_time(script)
                now_day = datetime.datetime.now().day
                script_start_day = datetime.datetime.strptime(script_start_time, '%Y-%m-%dT%H:%M:%SZ').day
                print('script_start_day: {}, now_day: {}'.format(script_start_day, now_day))
                if now_day != script_start_day:
                    self.kill_process_by_id_list(pid_list)
                    self.start_process(scrip_file_path, log_file_path, script)
                continue
            if is_stop or len(pid_list) > 1:
                self.kill_process_by_id_list(pid_list)
            if not is_stop:
                self.start_process(scrip_file_path, log_file_path, script)


if __name__ == '__main__':
    script_manager = ScriptManager()
    while True:
        try:
            script_manager.run()
            time.sleep(30)
        except redis.exceptions.ConnectionError:
            print('redis.exceptions.ConnectionError, sleep: {}'.format(120))
            time.sleep(120)
