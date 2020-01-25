import datetime
import json
import os
import pathlib
import tempfile
try:
    import texttable
except ImportError:
    texttable = None

from .object_full_name import object_full_name


class ObjectArrayStorage:
    """
    Store one or more objects on disk of the same object type.
    Implementation note: the objects are stored in JSON format.
    """
    def __init__(self, object_class, *, target: pathlib.Path = None):
        """
        Initialize the object.
        :param object_class: The object class expected for all append() calls.
        :param target: The target directory or file.
        """
        self._fh = None
        self._object_class = object_class
        self._path = target

        if not (hasattr(object_class, 'oas_fields') and
                hasattr(object_class, 'oas_version')):
            raise ValueError(
                "object_class does not support ObjectArrayStorage")

        if self._path is None:
            self._path = pathlib.Path(tempfile.gettempdir())

    def append(self, item) -> None:
        """
        Store the item.
        If this method is called outside of a context manager,
        an exception is raised.

        :param item: An instance of the class self._object_class
        :return: None
        """
        if self._fh is None:
            raise RuntimeError(
                "append() called outside of context manager (e.g. `with`)")

        # Build a temp dictionary describing the row.
        temp = {}
        for field in self._object_class.oas_fields:
            name = field['name']
            temp[name] = getattr(item, name)
            if hasattr(temp[name], '__members__'):
                # An Enum, or Enum-like thing.
                temp[name] = temp[name].name

        text_to_write = ',\n{}'.format(json.dumps(temp)).encode('utf-8')
        # ... and write the line.
        self._fh.write(text_to_write)
        self._write_file_trailer()

    @property
    def path(self) -> pathlib.Path:
        """
        Return the directory path or file path for storage.

        If the Context Manager has not yet been used, then the path
        only returns the path to the target directory.

        If the Context Manager has been used, then the path returned
        is the path to the storage file.
        :return: The target directory or file path.
        """
        return self._path

    def __enter__(self):
        """
        Initialize the context manager and open the file handle.
        :return: self
        """
        if self.path.is_dir():
            self._fh = tempfile.NamedTemporaryFile(
                delete=False, suffix='.json', dir=self.path,
                prefix=self. _object_class.__name__.lower() + '_')
            self._path = pathlib.Path(self._fh.name)
            self._initialize_file()
        elif self.path.is_file():
            self._fh = open(str(self.path), 'rb+')

        self._fh.__enter__()
        self._set_file_pos_to_array_close()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and close the file, if open.
        """
        result = None
        if self._fh:
            result = self._fh.__exit__(exc_type, exc_val, exc_tb)
            self._fh = None
        return result

    def __str__(self) -> str:
        """
        Load items from the object file and display them using texttable.
        :param path: The path to the file
        :return:
        """
        if not (self.path.is_file() and texttable):
            return ""

        with open(self.path) as fp:
            data = json.load(fp)
        if 1 >= len(data):
            raise ValueError("Invalid JSON file '{}'".format(self.path))
        overview = data[0]
        header = data[0]['fields']
        data = data[1:]

        class_version = self._object_class.oas_version
        if class_version != overview["version"]:
            raise RuntimeError(
                "File import version mismatch: {} != {}".format(
                    class_version, overview["version"]))

        table = texttable.Texttable()

        # Set data types for each column.
        data_types = list()
        for column in header:

            texttable_data_type = 'a'
            if 'tt_dtype' in column:
                texttable_data_type = column['tt_dtype']
                if texttable_data_type == 'daystamp':
                    texttable_data_type = self._daystamp
            data_types.append(texttable_data_type)

        table.set_cols_dtype(data_types)
        table.set_max_width(120)

        # If there are more than 100 rows, drop the horizontal lines.
        if 100 < len(data):
            formats = texttable.Texttable
            table.set_deco(formats.HEADER | formats.BORDER | formats.VLINES)

        fields = self._object_class.oas_fields
        table.header([item['name'] for item in header])
        for row in data:
            row_data = list()
            for column in header:
                temp = row[column['name']]
                if 'fmt' in column:
                    temp = column['fmt'].format(temp)
                row_data.append(temp)
            table.add_row(row_data)
        return table.draw()

    @staticmethod
    def _daystamp(time_since_epoch: float):
        """
        Return a time-since-epoch value as a HH:MM:SS.XXX string
        :param timestamp: The time since epoch.
        :return: The string.
        """
        return datetime.datetime.fromtimestamp(
            time_since_epoch).strftime('%H:%M:%S.%f')[:-3]

    def _initialize_file(self) -> None:
        """
        Write the header and first records to the file handle for an empty file.
        :return: None
        """

        version = self._object_class.oas_version
        fields = self._object_class.oas_fields
        dict_data = dict(
            class_name=object_full_name(self._object_class),
            version=version,
            fields=fields
            )
        data = json.dumps([dict_data, ])
        self._fh.write(data.encode('utf-8'))
        self._set_file_pos_to_array_close()

    def _set_file_pos_to_array_close(self) -> None:
        """
        Search the file backwards to the array close bracket.
        :return: None
        """
        if self._fh is None:
            raise RuntimeError(
                "append() called outside of context manager (e.g. `with`)")
        self._fh.seek(0, os.SEEK_END)
        pos = self._fh.tell()
        char = None
        while char != b']' and pos != 0:
            pos -= 1
            self._fh.seek(pos)
            char = self._fh.read(1)
        self._fh.seek(pos)

    def _write_file_trailer(self, *, trailer_text: str = ']\n') -> None:
        """
        Write the closing end of array and file, and reset the file position
        to the previous location.
        :param trailer_text: The text to use as an overwrite-able trailer.
            Defaults to a generally-useful value of ']\n'
        :return: None
        """
        # The data in the file up to this point needs to remain.  The
        # remainder will be overwritten as we add items.
        overwrite_pos = self._fh.tell()
        self._fh.write(trailer_text.encode('utf-8'))

        # Move back to where the next write should start.
        self._fh.seek(overwrite_pos)
