# -*- coding: utf-8 -*-
import datetime
from io import StringIO
import os
import re
from time import sleep
import unittest
from src.buscar_solotodo import Buscador as BuscadorSoloTodo
from src.get_displaylag_tellys import get_displaylag_screens, get_squidoo_monitors
from src.memoize_function_deco import file_memoized
from src.print_urls_table import imprimirTabla


class PruebaConBuscador(unittest.TestCase):
    # http://selenium-python.readthedocs.io/getting-started.html#using-selenium-to-write-tests
    def setUp(self):
        self.buscador = BuscadorSoloTodo()

    def tearDown(self):
        self.buscador.cerrar_navegador()


class PruebaSolotodo(PruebaConBuscador):
    def test_trae_cualquier_cosa(self):
        "Va a buscar algo (lo que sea)"
        resultados = self.buscador.buscar("usb")
        self.assertTrue(resultados)

    def test_trae_uno(self):
        """Va a buscar algo (monitor de verdad)

        Es necesario que la búsqueda entregue un ítem existente"""
        resultados = self.buscador.buscar("VE228H")
        self.assertTrue(resultados)

    def test_sin_resultados(self):
        resultados = self.buscador.buscar("potopichicaca")
        self.assertFalse(resultados)

    def test_sin_basura(self):
        '''Busca un monitor que _sé_ que no está y filtra la basura'''
        resultados = self.buscador.buscar("IPS277L-BN")
        self.assertFalse(resultados)

    def test_no_sacar_lo_que_no_es_basura(self):
        '''No filtrar de más

        Sé que (probablemente) ⎡25UM58-P⎦ no es lo mismo que ⎡25UM58⎦,
        pero la idea es revisar el filtrado automático.

        De ahí el humano al otro lado de la tantalla decidirá si
        el filtrado pasó algo incorrecto.
        '''
        resultados = self.buscador.buscar("25UM58-P")
        self.assertTrue(resultados)


class PruebaParserDisplayLag(unittest.TestCase):
    def test_formato(self):
        '''Revisa el formato de los resultados.'''
        pantallas = get_displaylag_screens()
        for pantalla in pantallas:
            for etiqueta in ['brand',
                             'size',
                             'modelo',
                             'resolution',
                             'screen_type',
                             'input_lag']:
                self.assertIn(etiqueta, pantalla)
            self.assertIsNotNone(re.match(r'^[0-9.]+ms$',
                                          pantalla['input_lag']),
                                 "No encontré input_lag en {pantalla}"
                                 .format(pantalla=pantalla))
            self.assertIsNotNone(re.match(r'^[0-9.]+"?$', pantalla['size']),
                                 "No encontré 'size' en {pantalla}"
                                 .format(pantalla=pantalla))

    def test_formato_squidoo(self):
        '''Pantallas específicas'''
        for pantalla in get_squidoo_monitors():
            self.assertIsNotNone(re.match(r'^[0-9.]+ms$',
                                          pantalla['input_lag']),
                                          "Sin input_lag en {modelo}"
                                          .format(modelo=pantalla["modelo"]))


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
        self.assertEqual(f.getvalue(), '''|a | b | c |
|1 | 2 |  |
|α | β | γ | δ
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
        ahora = datetime.datetime.now

        entrada = 'bbb'
        try:
            os.remove(file_memoized(lambda x: x).getCacheFile(entrada))
        except FileNotFoundError:
            pass

        inicio = ahora()
        # no ocupa cache, espera 2s
        r1 = capitalize(entrada)
        δ1 = ahora() - inicio
        self.assertGreater(δ1, Δ(seconds=1),
                           "{} debió ser > 1s".format(δ1))

        inicio = ahora()
        # ocupa cache, respuesta inmediata
        r2 = capitalize(entrada)
        δ2 = ahora() - inicio
        assert δ2 < Δ(seconds=1)

        self.assertEqual(r1, r2)


if __name__ == '__main__':
    unittest.main()
