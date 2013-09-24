#
# Copyright (c) 2013 Intel, Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc., 59
# Temple Place - Suite 330, Boston, MA 02111-1307, USA.

""" This logging module is fully compatible with the old msger module, and
    it supports interactive mode, logs the messages with specified levels
    to specified stream, can also catch all error messages including the
    involved 3rd party modules to the logger
"""

import os
import sys
import logging
import tempfile

__ALL__ = [
    'get_loglevel',
    'set_loglevel',
    'set_logfile',
    'enable_interactive',
    'disable_interactive',
    'enable_logstderr',
    'disable_logstderr',
    'raw',
    'debug',
    'verbose',
    'info',
    'warning',
    'error',
    'select',
    'choice',
    'ask',
    'pause',
]


# define the color constants
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)

# color sequence for tty terminal
COLOR_SEQ = "\033[%dm"  # pylint: disable=W1401
# reset sequence for tty terminal
RESET_SEQ = "\033[0m" # pylint: disable=W1401

# new log level
RAWTEXT = 25
VERBOSE = 15

# define colors for log levels
COLORS = {
    'DEBUG':    COLOR_SEQ % BLUE,
    'VERBOSE':  COLOR_SEQ % MAGENTA,
    'INFO':     COLOR_SEQ % GREEN,
    'WARNING':  COLOR_SEQ % YELLOW,
    'ERROR':    COLOR_SEQ % RED,
}


class LevelFilter(logging.Filter):
    """ A filter that selects logging message with specified level """
    def __init__(self, levels):  # pylint: disable=W0231
        self._levels = levels

    def filter(self, record):
        if self._levels:
            return record.levelname in self._levels
        return False


class MicStreamHandler(logging.StreamHandler):
    """ A stream handler that print colorized levelname in tty terminal """
    def __init__(self, stream=None):
        logging.StreamHandler.__init__(self, stream)
        msg_fmt = "%(color)s%(levelname)s:%(reset)s %(message)s"
        self.setFormatter(logging.Formatter(fmt=msg_fmt))

    def _use_color(self):
        """ Check if to print in color or not """
        in_emacs = (os.getenv("EMACS") and
                    os.getenv("INSIDE_EMACS", "").endswith(",comint"))
        return self.stream.isatty() and not in_emacs

    def format(self, record):
        """ Format the logging record if need color """
        record.color = record.reset = ""
        if self._use_color():
            record.color = COLORS[record.levelname]
            record.reset = RESET_SEQ
        return logging.StreamHandler.format(self, record)


class RedirectedStderr(object):
    """ A faked error stream that redirect stderr to a temp file """
    def __init__(self):
        self.tmpfile = tempfile.NamedTemporaryFile()
        self.fderr = None
        self.value = None

    def __del__(self):
        self.close()

    def close(self):
        """ Close the temp file and clear the buffer """
        try:
            self.value = None
            self.tmpfile.close()
        except OSError:
            pass

    def truncate(self):
        """ Truncate the tempfile to size zero """
        if self.tmpfile:
            os.ftruncate(self.tmpfile.fileno(), 0)

    def redirect(self):
        """ Redirect stderr to the temp file """
        self.fderr = os.dup(2)
        os.dup2(self.tmpfile.fileno(), 2)

    def restore(self):
        """ Restore the stderr and read the bufferred data """
        os.dup2(self.fderr, 2)
        self.fderr = None

        if self.tmpfile:
            self.tmpfile.seek(0, 0)
            self.value = self.tmpfile.read()

    def getvalue(self):
        """ Read the bufferred data """
        if self.tmpfile:
            self.tmpfile.seek(0, 0)
            self.value = self.tmpfile.read()
            os.ftruncate(self.tmpfile.fileno(), 0)
            return self.value
        return None

class MicFileHandler(logging.FileHandler):
    """ This file handler is supposed to catch the stderr output from
        all modules even 3rd party modules involed, as it redirects
        the stderr stream to a temp file stream, if logfile assigned,
        it will flush the record to file stream, else it's a buffer
        handler; once logfile assigned, the buffer will be flushed
    """
    def __init__(self, filename=None, mode='w', encoding=None, capacity=10):
        # we don't use FileHandler to initialize,
        # because filename might be expected to None
        logging.Handler.__init__(self)
        self.stream = None
        if filename:
            self.baseFilename = os.path.abspath(filename)
        else:
            self.baseFilename = None
        self.mode = mode
        self.encoding = None
        self.capacity = capacity
        # buffering the records
        self.buffer = []

        # set formater locally
        msg_fmt = "[%(asctime)s] %(message)s"
        date_fmt = "%m/%d %H:%M:%S %Z"
        self.setFormatter(logging.Formatter(fmt=msg_fmt, datefmt=date_fmt))
        self.olderr = sys.stderr
        self.stderr = RedirectedStderr()
        self.errmsg = None

    def set_logfile(self, filename, mode='w'):
        """ Set logfile path to make it possible flush records not-on-fly """
        self.baseFilename = os.path.abspath(filename)
        self.mode = mode

    def redirect_stderr(self):
        """ Start to redirect stderr for catching all error output """
        self.stderr.redirect()

    def restore_stderr(self):
        """ Restore stderr stream and log the error messages to both stderr
            and log file if error messages are not empty
        """
        self.stderr.restore()
        self.errmsg = self.stderr.value
        if self.errmsg:
            self.logstderr()

    def logstderr(self):
        """ Log catched error message from stderr redirector """
        if not self.errmsg:
            return

        sys.stdout.write(self.errmsg)
        sys.stdout.flush()

        record = logging.makeLogRecord({'msg': self.errmsg})
        self.buffer.append(record)

        # truncate the redirector for the errors is logged
        self.stderr.truncate()
        self.errmsg = None

    def emit(self, record):
        """ Emit the log record to Handler """
        # if there error message catched, log it first
        self.errmsg = self.stderr.getvalue()
        if self.errmsg:
            self.logstderr()

        # if no logfile assigned, it's a buffer handler
        if not self.baseFilename:
            self.buffer.append(record)
            if len(self.buffer) >= self.capacity:
                self.buffer = []
        else:
            self.flushing(record)

    def flushing(self, record=None):
        """ Flush buffer and record to logfile """
        # NOTE: 'flushing' can't be named 'flush' because of 'emit' calling it
        # set file stream position to SEEK_END(=2)
        if self.stream:
            self.stream.seek(0, 2)
        # if bufferred, flush it
        if self.buffer:
            for arecord in self.buffer:
                logging.FileHandler.emit(self, arecord)
            self.buffer = []
        # if recorded, flush it
        if record:
            logging.FileHandler.emit(self, record)

    def close(self):
        """ Close handler after flushing the buffer """
        # if any left in buffer, flush it
        if self.stream:
            self.flushing()
        logging.FileHandler.close(self)


class MicLogger(logging.Logger):
    """ The MIC logger class, it supports interactive mode, and logs the
        messages with specified levels tospecified stream, also can catch
        all error messages including the involved 3rd party modules
    """
    def __init__(self, name, level=logging.INFO):
        logging.Logger.__init__(self, name, level)
        self.interactive = True
        self.logfile = None
        self._allhandlers = {
            'default': logging.StreamHandler(sys.stdout),
            'stdout': MicStreamHandler(sys.stdout),
            'stderr': MicStreamHandler(sys.stderr),
            'logfile': MicFileHandler(),
        }

        self._allhandlers['default'].addFilter(LevelFilter(['RAWTEXT']))
        self._allhandlers['default'].setFormatter(
            logging.Formatter(fmt="%(message)s"))
        self.addHandler(self._allhandlers['default'])

        self._allhandlers['stdout'].addFilter(LevelFilter(['DEBUG', 'VERBOSE',
                                                          'INFO']))
        self.addHandler(self._allhandlers['stdout'])

        self._allhandlers['stderr'].addFilter(LevelFilter(['WARNING',
                                                           'ERROR']))
        self.addHandler(self._allhandlers['stderr'])

        self.addHandler(self._allhandlers['logfile'])

    def set_logfile(self, filename, mode='w'):
        """ Set logfile path """
        self.logfile = filename
        self._allhandlers['logfile'].set_logfile(self.logfile, mode)

    def enable_logstderr(self):
        """ Start to log all error messages """
        if self.logfile:
            self._allhandlers['logfile'].redirect_stderr()

    def disable_logstderr(self):
        """ Stop to log all error messages """
        if self.logfile:
            self._allhandlers['logfile'].restore_stderr()

    def verbose(self, msg, *args, **kwargs):
        """ Log a message with level VERBOSE """
        if self.isEnabledFor(VERBOSE):
            self._log(VERBOSE, msg, args, **kwargs)

    def raw(self, msg, *args, **kwargs):
        """ Log a message in raw text format """
        if self.isEnabledFor(RAWTEXT):
            self._log(RAWTEXT, msg, args, **kwargs)

    def select(self, msg, optdict, default=None):
        """ Log a message in interactive mode """
        if not optdict.keys():
            return default
        if default is None:
            default = optdict.keys()[0]
        msg += " [%s](%s): " % ('/'.join(optdict.keys()), default)
        if not self.interactive or self.logfile:
            reply = default
            self.raw(msg + reply)
        else:
            while True:
                reply = raw_input(msg).strip()
                if not reply or reply in optdict:
                    break
            if not reply:
                reply = default
        return optdict[reply]


def error(msg):
    """ Log a message with level ERROR on the MIC logger """
    LOGGER.error(msg)
    sys.exit(2)

def warning(msg):
    """ Log a message with level WARNING on the MIC logger """
    LOGGER.warning(msg)

def info(msg):
    """ Log a message with level INFO on the MIC logger """
    LOGGER.info(msg)

def verbose(msg):
    """ Log a message with level VERBOSE on the MIC logger """
    # pylint: disable=E1103
    LOGGER.verbose(msg)

def debug(msg):
    """ Log a message with level DEBUG on the MIC logger """
    LOGGER.debug(msg)

def raw(msg):
    """ Log a message on the MIC logger in raw text format"""
    # pylint: disable=E1103
    LOGGER.raw(msg)

def select(msg, optdict, default=None):
    """ Show an interactive scene in tty terminal and
        logs them on MIC logger
    """
    # pylint: disable=E1103
    return LOGGER.select(msg, optdict, default)

def choice(msg, optlist, default=0):
    """ Give some alternatives to users for answering the question """
    # pylint: disable=E1103
    return LOGGER.select(msg, dict(zip(optlist, optlist)), optlist[default])

def ask(msg, ret=True):
    """ Ask users to answer 'yes' or 'no' to the question """
    answers = {'y': True, 'n': False}
    default = {True: 'y', False: 'n'}[ret]
    # pylint: disable=E1103
    return LOGGER.select(msg, answers, default)

def pause(msg=None):
    """ Pause for any key """
    if msg is None:
        msg = "press ANY KEY to continue ..."
    raw_input(msg)

def set_logfile(logfile, mode='w'):
    """ Set logfile path to the MIC logger """
    # pylint: disable=E1103
    LOGGER.set_logfile(logfile, mode)

def set_loglevel(level):
    """ Set loglevel to the MIC logger """
    if isinstance(level, basestring):
        level = logging.getLevelName(level)
    LOGGER.setLevel(level)

def get_loglevel():
    """ Get the loglevel of the MIC logger """
    return logging.getLevelName(LOGGER.level)

def disable_interactive():
    """ Disable the interactive mode """
    LOGGER.interactive = False

def enable_interactive():
    """ Enable the interactive mode """
    LOGGER.interactive = True

def set_interactive(value):
    """ Set the interactive mode (for compatibility) """
    if value:
        enable_interactive()
    else:
        disable_interactive()

def enable_logstderr(fpath=None):  # pylint: disable=W0613
    """ Start to log all error message on the MIC logger """
    # pylint: disable=E1103
    LOGGER.enable_logstderr()

def disable_logstderr():
    """ Stop to log all error message on the MIC logger """
    # pylint: disable=E1103
    LOGGER.disable_logstderr()


# add two level to the MIC logger: 'VERBOSE', 'RAWTEXT'
logging.addLevelName(VERBOSE, 'VERBOSE')
logging.addLevelName(RAWTEXT, 'RAWTEXT')
# initial the MIC logger
logging.setLoggerClass(MicLogger)
LOGGER = logging.getLogger("MIC")
