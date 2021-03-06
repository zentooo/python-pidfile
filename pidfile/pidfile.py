import os
import psutil


class AlreadyRunningError(Exception):
    pass


class PIDFile(object):
    def __init__(self, filename='pidfile', replace=False):
        self._process_name = psutil.Process(os.getpid()).cmdline()[0]
        self._file = filename
        self._replace = replace

    @property
    def is_running(self):
        if not os.path.exists(self._file):
            return False

        with open(self._file, "r") as f:
            try:
                pid = int(f.read())
            except (OSError, ValueError):
                return False

        if not psutil.pid_exists(pid):
            return False

        try:
            cmd1 = psutil.Process(pid).cmdline()[0]
            return cmd1 == self._process_name
        except psutil.AccessDenied:
            return False

    def __enter__(self):
        if self._replace and os.path.exists(self._file):
            with open(self._file, "r") as f:
                try:
                    pid = int(f.read())
                    process = psutil.Process(pid)
                    process.kill()
                except (OSError, ValueError, psutil.NoSuchProcess):
                    pass

        elif self.is_running:
            raise AlreadyRunningError

        with open(self._file, "w") as f:
            f.write(str(os.getpid()))

        return self

    def __exit__(self, *args):
        if os.path.exists(self._file):
            try:
                os.remove(self._file)
            except OSError:
                pass
