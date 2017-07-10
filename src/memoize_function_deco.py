''' Memoize value to/from disk

Based off https://wiki.python.org/moin/PythonDecoratorLibrary
'''
import os
import collections
import pickle
import hashlib
import datetime


class file_memoized(object):
    def __init__(self, timeout=datetime.timedelta(days=30)):
        '''Default timeout for cache: 30 days
        '''
        self._func = None
        self._timeout = timeout

    def file_is_too_old(self, file_path):
        return datetime.datetime.now() \
                - datetime.datetime.fromtimestamp(
                    os.path.getctime(file_path)) \
                > self._timeout

    def __call__(self, func):
        def sub_call(*args):
            if not isinstance(args, collections.Hashable):
                # uncacheable sa a list
                return func(*args)
            file_path = self.getCacheFile(args)
            if os.path.exists(file_path) \
                    and not self.file_is_too_old(file_path):
                with open(file_path, mode='rb') as cacheFile:
                    r = pickle.load(cacheFile)
                    return r
                raise RuntimeError("Shouldn't be here")
            else:
                # non-cached run
                r = func(*args)
                try:
                    os.makedirs(os.path.dirname(file_path))
                except FileExistsError:
                    pass
                with open(self.getCacheFile(args), mode='wb') as outFile:
                    pickle.dump(r, outFile)
                    return r
        return sub_call

    def getCacheFile(self, _args):
        return os.path.join('.', '.memocache',
                            hashlib.sha1(
                                bytes(str(_args), 'utf-8')).hexdigest())

