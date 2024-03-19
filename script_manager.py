import os, signal, time, redis
from redis import StrictRedis

PARENT_PATH = '/home/stocks'


class ScriptManager(object):
    def __init__(self):
        self.scrip_list = [
            {'name': 'monitor_1', 'redis_prefix': 'monitor_1'},
            {'name': 'monitor_2', 'redis_prefix': 'monitor_2'},
            {'name': 'notifier_1', 'redis_prefix': 'monitor_1'},
            {'name': 'notifier_2', 'redis_prefix': 'monitor_2'},
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

    def start_process(self, scrip_file_path, log_file_path):
        start_cmd = 'nohup python3 -u {} >{} 2>&1 &'.format(scrip_file_path, log_file_path)
        print('start_cmd: {}'.format(start_cmd))
        start_cmd_result = os.system(start_cmd)
        print('start_cmd_result: {}'.format(start_cmd_result))

    def get_script_stop_status(self, script):
        key = '{}:is_stop'.format(script['redis_prefix'])
        is_stop = self.redis.get(key)
        if is_stop is None:
            is_stop = 0
            self.redis.set(key, is_stop)
        return int(is_stop)

    def run(self):
        logs_path = '{}/logs'.format(PARENT_PATH)
        for script in self.scrip_list:
            scrip_name = script['name']
            py_name = '{}.py'.format(scrip_name)
            pid_list = self.get_pid_list_by_name(py_name)
            print('py_name: {}, {} scripts is running...'.format(py_name, len(pid_list)))
            if len(pid_list) == 1:
                continue
            if len(pid_list) > 1:
                for p_id in pid_list:
                    self.kill_process_by_pid(p_id)
            is_stop = self.get_script_stop_status(script)
            if not is_stop:
                scrip_file_path = '{}/{}'.format(PARENT_PATH, py_name)
                log_file_path = '{}/{}.log'.format(logs_path, scrip_name)
                self.start_process(scrip_file_path, log_file_path)

            # self.set_redis_script_stop_status(script, stop_status=1)
            # pid_list = self.get_pid_list_by_name(py_name)
            # print(pid_list)
            # if len(pid_list) != 0:
            #     for p_id in pid_list:
            #         self.kill_process_by_pid(p_id)
            # pid_list = self.get_pid_list_by_name(py_name)
            # scrip_file_path = '{}/{}'.format(PARENT_PATH, py_name)
            # if len(pid_list) == 0:
            #     for _ in range(parallels):
            #         log_file_path = '{}/{}.log'.format(logs_path, scrip_name)
            #         self.start_process(scrip_file_path, log_file_path)
            #     if parallels != 0:
            #         print('py_name: {}, restarted {} scripts'.format(py_name, parallels))
            #     self.set_redis_script_stop_status(script, stop_status=0)
            # print('-----------script end-----------')


if __name__ == '__main__':
    script_manager = ScriptManager()
    while True:
        try:
            script_manager.run()
            time.sleep(30)
        except redis.exceptions.ConnectionError:
            print('redis.exceptions.ConnectionError, sleep: {}'.format(120))
            time.sleep(120)
