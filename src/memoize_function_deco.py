''' Memoize value to/from disk

Based off https://wiki.python.org/moin/PythonDecoratorLibrary
'''
import os
import collections
import pickle
import hashlib
import datetime

class file_memoized(object):
    def __init__(self, timeout=datetime.timedelta(30,0,0)):
        '''Default timeout for cache: 30 days
        '''
        self._func = None
        self._timeout = timeout

    def file_is_too_old(self, file_path):
        return datetime.datetime.now() \
                - datetime.datetime.fromtimestamp(os.path.getctime(file_path)) \
                > self._timeout

    def __call__(self, func):
        def sub_call(*args):
            if not isinstance(args, collections.Hashable):
                #uncacheable sa a list
                return func(*args)
            file_path = self.getCacheFile(args)
            if os.path.exists(file_path) \
                    and not self.file_is_too_old(file_path):
                with open(file_path,mode='rb') as cacheFile:
                    r = pickle.load(cacheFile)
                    return r
                raise Error("Shouldn't be here")
            else:
                r = func(*args)
                try:
                    os.makedirs( os.path.dirname(file_path))
                except FileExistsError:
                    pass
                with open(self.getCacheFile(args),mode='wb') as outFile:
                    pickle.dump(r, outFile)
                    return r
        return sub_call

    def getCacheFile(self, _args):
        return os.path.join('.','.memocache', \
                hashlib.sha1( \
                    bytes(str(_args), 'utf-8')).hexdigest())

if __name__ == '__main__':
    @file_memoized(datetime.timedelta(0,0,1))
    def capitalize(s):
        return s.upper()
    try:
        os.remove(file_memoized(lambda x: x).getCacheFile('aaa'))
    except FileNotFoundError:
        pass
    r0 = capitalize('aaa')
    r1 = capitalize('aaa')

    assert r0 == r1

    @file_memoized()
    def noargs():
        return 1
    assert noargs() == noargs()
