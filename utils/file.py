import gzip
import io
import os
from contextlib import contextmanager


@contextmanager
def safe_reading(file):
    """
    context manager to read file, it backups the current seek position and set it to start
    later resets the position to backed up point
    """
    old_file_position = file.tell()
    file.seek(0, os.SEEK_END)
    yield
    file.seek(old_file_position, os.SEEK_SET)


def file_size(file) -> int:
    """
    :returns file size in bytes
    """
    size = getattr(file, '_size', None)
    if size is not None:
        return size

    with safe_reading(file):
        return file.tell()


class CSVFileCompressionMixin:
    """
    Given a csv file, it uses gzip to return its compressed package
    """

    # max limit on file size in bytes after which file must be compressed
    ENFORCE_COMPRESSION_FILE_SIZE = 10 * 1048576    # 10 MB

    def compress(self, file):
        """
        accepts a file and returns its compressed GZIP buffer
        """

        buffer = io.BytesIO()
        with gzip.GzipFile(mode='w', fileobj=buffer) as z_file:
            for line in file:
                z_file.write(line.encode('utf-8'))
        buffer.seek(0, os.SEEK_SET)
        return buffer

    def conditional_compress(self, file, force=False):
        """
        if self.should_compress or force is True, returns (True, compressed file) otherwise (False, original file)

        """
        if force or self.should_compress(file):
            compressed = True
            new_file = self.compress(file)
        else:
            compressed = False
            new_file = file
        return compressed, new_file

    def should_compress(self, file) -> bool:
        return file_size(file) >= self.ENFORCE_COMPRESSION_FILE_SIZE
