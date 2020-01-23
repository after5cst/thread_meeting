from thread_meeting import transcriber

import importlib
import json
import pathlib
import tempfile
import texttable
import unittest

if __name__ == '__main__':
    from worker import Worker
    from worker import WorkerState
else:
    from .worker import Worker
    from .worker import WorkerState


import os


# https://stackoverflow.com/questions/2020014/get-fully-qualified-class-name-of-an-object-in-python
def fullname(o):
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__
    return module + '.' + o.__class__.__name__


#taken from https://stackoverflow.com/questions/18857352/python-remove-very-last-character-in-file
def truncate_utf8_chars(filename, count, ignore_newlines=True) -> str:
    """
    Truncates last `count` characters of a text file encoded in UTF-8.
    :param filename: The path to the text file to read
    :param count: Number of UTF-8 characters to remove from the end of the file
    :param ignore_newlines: Set to true, if the newline character at the end of the file should be ignored
    """
    with open(filename, 'rb+') as f:
        last_char = None

        size = os.fstat(f.fileno()).st_size

        offset = 1
        chars = 0
        while offset <= size:
            f.seek(-offset, os.SEEK_END)
            b = ord(f.read(1))

            if ignore_newlines:
                if b == 0x0D or b == 0x0A:
                    offset += 1
                    continue

            if b & 0b10000000 == 0 or b & 0b11000000 == 0b11000000:
                # This is the first byte of a UTF8 character
                chars += 1
                if chars == count:
                    # When `count` number of characters have been found, move current position back
                    # with one byte (to include the byte just checked) and truncate the file
                    f.seek(-1, os.SEEK_CUR)
                    f.truncate()
                    return


def write_data(data, dir_name) -> pathlib.Path:
    """
    Write the provided data to the related output file.
    :param data: The data object.
    :param dir_name: The directory where the file should exist.
    :return: The path to the file that was written.
    """
    version = data._log_version
    fields = data._log_fields
    class_name = str(type(data).__name__)

    # Get the last piece of the class name.
    class_name = class_name[class_name.rfind('.')+1:]
    file_name = "{class_name}.dat".format(
        class_name=class_name,).lower()

    # If the file does not exist, create one and write the header.
    path = pathlib.Path(dir_name) / file_name
    if not path.is_file():
        with open(path, "w") as fp:
            fp.write('[' + json.dumps(
                dict(class_name=fullname(data), version=version)) +
                ',\n')
            fp.write(json.dumps(fields) + ']\n')

    # Truncate the file at the last character (it should be a ']')
    truncate_utf8_chars(path, 1)

    with open(path, "a+") as fp:
        # The truncate ended the file, so add ',\n' to the end
        # to make a continuation.
        fp.write(',\n')
        # Now convert the data to a dict for writing.
        temp = dict()
        for field in fields:
            name = field['name']
            temp[name] = getattr(data, name)
            if hasattr(temp[name], '__members__'):
                # An Enum, or Enum-like thing.
                temp[name] = temp[name].name
        # ... and write the line.
        fp.write(json.dumps(temp) + ']\n')

    return path


def show_file_as_table(path: pathlib.Path):
    """
    Load items from the object file and display them using texttable.
    :param path: The path to the file
    :return:
    """
    with open(path) as fp:
        data = json.load(fp)
    if 2 >= len(data):
        raise ValueError("Invalid JSON file '{}'".format(path))
    overview = data[0]
    header = data[1]
    data = data[2:]

    # Import the string.
    full_class_name = overview["class_name"]
    class_items = full_class_name.split('.')
    class_name = class_items[-1]
    class_path = '.'.join(class_items[:-1])
    module = importlib.import_module(class_path)
    class_object = getattr(module, class_name)
    class_version = class_object._log_version
    if class_version != overview["version"]:
        raise RuntimeError("File import version mismatch: {} != {}".format(
            class_version, overview["version"]))

    table = texttable.Texttable()

    # Set data types for each column.
    data_types = list()
    for column in header:
        if 'tt_dtype' in column:
            data_types.append(column['tt_dtype'])
        else:
            data_types.append('a')
    table.set_cols_dtype(data_types)
    table.set_max_width(120)

    # If there are more than 100 rows, drop the horizontal lines.
    if 100 < len(data):
        formats = texttable.Texttable
        table.set_deco(formats.HEADER | formats.BORDER | formats.VLINES)

    fields = class_object._log_fields
    printed = False
    table.header([item['name'] for item in header])
    for row in data:
        row_data = list()
        for column in header:
            temp = row[column['name']]
            if 'fmt' in column:
                temp = column['fmt'].format(temp)
                if not printed:
                    print(temp, type(temp))
                    printed = True
            row_data.append(temp)
        table.add_row(row_data)
    print(table.draw())



class BatonTest(unittest.TestCase):

    def test_can_send_message_to_worker(self):
        with transcriber() as transcript:
            queue = transcript  # Keep transcript from losing scope.
            workers = [Worker(name='worker') for i in range(2)]
            Worker.execute_meeting(*workers)
            # If we get here, then we managed to start the workers,
            # sent a start message, and the workers exited.
            # So, we sent a message to the worker(s).
            for worker in workers:
                self.assertTrue(worker.state == WorkerState.FINAL)

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            # tmp_dir_name = '/tmp'
            file_path = None
            while queue:
                entry = queue.get()
                file_path = write_data(entry, tmp_dir_name)
            if file_path:
                show_file_as_table(file_path)


if __name__ == '__main__':
    unittest.main()
