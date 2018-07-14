# -*- coding: utf-8 -*-
import datetime
from io import StringIO
import os
import re
from time import sleep
import unittest
from src.buscar_solotodo import buscar_solotodo
from src.get_displaylag_tellys import get_displaylag_screens
from src.memoize_function_deco import file_memoized
from src.print_urls_table import imprimirTabla


@file_memoized()
def cached_solotodo(*args, **kargs):
    return buscar_solotodo(*args, **kargs)


@file_memoized()
def cached_tellys(*args, **kargs):
    return get_displaylag_screens(*args, **kargs)


class PruebaSolotodo(unittest.TestCase):
    def test_trae(self):
        "Va a buscar algo (lo que sea)"
        resultados = cached_solotodo("usb")
        self.assertTrue(resultados)


class PruebaMonitorSolotodo(unittest.TestCase):
    def test_trae(self):
        """Va a buscar algo (monitor de verdad)

        Es necesario que la búsqueda entregue un ítem existente"""
        resultados = cached_solotodo("V196HQL")
        self.assertTrue(resultados)


class PruebaParserDisplayLag(unittest.TestCase):
    def test_formato(self):
        '''Revisa el formato de los resultados.'''
        pantallas = cached_tellys()
        for pantalla in pantallas:
            for etiqueta in ['brand',
                             'size',
                             'model',
                             'resolution',
                             'screen_type',
                             'input_lag']:
                self.assertIn(etiqueta, pantalla)
            self.assertIsNotNone(re.match(r'^\d{2}ms$', pantalla['input_lag']))
            self.assertIsNotNone(re.match(r'^[0-9.]+"$', pantalla['size']))


class ImprimirTabla(unittest.TestCase):
    def test_tablaImpresa(self):
        '''Formato correcto para la tabla'''
        urls = [
            ['a', 'b', 'c'],
            ['1', '2'],
            ['α', 'β', 'γ', 'δ'],
        ]
        f = StringIO()
        imprimirTabla(urls, f)
        self.assertEqual(f.getvalue(), '''|a|b|c|
|1|2||
|α|β|γ|δ
''')


class MemoCache(unittest.TestCase):
    def test_cache(self):
        '''Los valores se mantienen en cache'''
        @file_memoized(datetime.timedelta(seconds=3))
        def capitalize(s):
            return s.upper()
        try:
            os.remove(file_memoized(lambda x: x).getCacheFile('aaa'))
        except FileNotFoundError:
            pass
        r0 = capitalize('aaa')
        r1 = capitalize('aaa')

        self.assertEqual(r0, r1)

        @file_memoized()
        def noargs():
            return 1
        assert noargs() == noargs()

    def test_cargaValores(self):
        '''Ocupa el cache'''
        Δ = datetime.timedelta

        @file_memoized(Δ(seconds=3))
        def capitalize(s):
            sleep(Δ(seconds=2).total_seconds())
            return s.upper()
        now = datetime.datetime.now

        entrada = 'bbb'
        try:
            os.remove(file_memoized(lambda x: x).getCacheFile(entrada))
        except FileNotFoundError:
            pass

        inicio = now()
        δ1 = now() - inicio
        assert δ1 > Δ(seconds=1)

        inicio = now()
        δ2 = now() - inicio
        assert δ2 < Δ(seconds=1)


if __name__ == '__main__':
    unittest.main()
