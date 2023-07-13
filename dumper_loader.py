import json, codecs, pickle, os


class FileDataDumper(object):
    def __init__(self, file_path, mode, encoding='utf-8'):
        self.mode = mode
        self.file = codecs.open(file_path, mode, encoding=encoding)

    def dump_data_by_append(self, data, json_dumps=True):
        if json_dumps:
            line = json.dumps(data, ensure_ascii=False, default=str) + '\n'
        else:
            line = data + '\n'
        self.file.write(line)
        self.file.flush()

    def dump_data(self, data, json_dumps=True):
        json.dump(data, self.file)

    def dump_data_list_by_append(self, data_list, json_dumps=True):
        for data in data_list:
            line = json.dumps(data, ensure_ascii=False) + '\n'
            self.file.write(line)
        self.file.flush()

    def close(self):
        self.file.close()


def load_data_by_json_load(file_path, ret_type):
    try:
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            return json_data
    except Exception as e:
        return ret_type


def save_data_by_json_dump(file_path, json_data):
    try:
        with codecs.open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f)
    except Exception as e:
        print('save_data failed')


def save_data_append_by_json_dump(file_path, json_data):
    with codecs.open(file_path, 'a+', encoding='utf-8') as f:
        line = json.dumps(json_data, ensure_ascii=False) + '\n'
        f.write(line)


def save_data_list_append_by_json_dump(file_path, json_data_list):
    with codecs.open(file_path, 'a+', encoding='utf-8') as f:
        for json_data in json_data_list:
            line = json.dumps(json_data, ensure_ascii=False) + '\n'
            f.write(line)


def load_data_append_by_json_dump(file_path, ret_type, exception_raise=True):
    try:
        item_list = []
        file_size = os.path.getsize(file_path)
        gb_file_size = file_size/1024/1024/1024
        if gb_file_size > 1:
            print('file is large, size: {:.2f} GB, please use load_big_data_append_by_json_dump'.format(gb_file_size))
            return ret_type
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                try:
                    item = json.loads(line)
                except Exception as e:
                    print(line)
                    print(e)
                    if exception_raise:
                        raise e
                    else:
                        continue
                item_list.append(item)
            return item_list
    except Exception as e:
        print(e)
        return ret_type


def load_data_append_simple(file_path, ret_type):
    try:
        item_list = []
        file_size = os.path.getsize(file_path)
        gb_file_size = file_size/1024/1024/1024
        if gb_file_size > 1:
            print('file is large, size: {:.2f} GB, please use load_big_data_append_by_json_dump'.format(gb_file_size))
            return ret_type
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                # print(line)
                if not line:
                    print('ddd')
                item_list.append(line)
            return item_list
    except Exception as e:
        print(e)
        return ret_type


def load_big_data_append_by_json_dump(file_path, ret_type):
    try:
        error_count = 0
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            line_number = 0
            while True:
                line = f.readline()
                line_number += 1
                if line:
                    try:
                        item = eval(line)
                        # item = json.loads(line, strict=False)
                    except Exception as e:
                        print(e)
                        error_count += 1
                        print('error_count: {}'.format(error_count))
                        continue
                    yield item
                else:
                    print('total_line_number: {}'.format(line_number))
                    break
    except Exception as e:
        print(e)
        return ret_type


def generate_csv_by_items(output_file_path, items):
    import csv
    keys = None
    data_list = []
    for item in items:
        if not keys:
            keys = item.keys()
            data_list.append(list(keys))
        data_list.append([item[key] for key in keys])
    with open(output_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data_list)




