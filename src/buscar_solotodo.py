# -*- coding: utf-8 -*-
''' Buscar en http://www.solotodo.com/
'''
import contextlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import warnings


class imagen_cargada(object):
    """Revisa que imágenes en un XPath esten cargadas

    https://stackoverflow.com/a/42661603"""
    def __init__(self, localizador):
        self.localizador = localizador

    def _imagen_cargada(self, navegador, elemento):
        _js = "return arguments[0].complete"
        return navegador.execute_script(_js, elemento)

    def __call__(self, navegador):
        elementos = navegador.find_elements(*self.localizador)
        if not elementos:
            # todavía no se carga el DOM de la imagen
            return False
        imágenes_sin_cargar = [not self._imagen_cargada(navegador, e)
                               for e in elementos]
        if any(imágenes_sin_cargar):
            # alguna imagen no está cargada
            return False
        # todo listo
        return elementos


class resultados_listos(object):
    """Revisa que resultados estén cargados
    Revisa que se complete una de dos situaciones:
        - No hay resultados
        - Los resultados están cargados (si y solo si sus imágenes están
        cargadas)"""

    def __init__(self, localizador):
        self.imágenes_cargadas = imagen_cargada(localizador)

    def __call__(self, navegador):
        div_sin_resultados = (
                navegador
                .find_elements_by_xpath(
                    "//div[@class='category-browse-no-results']"))
        if div_sin_resultados:
            return div_sin_resultados  # avisar explícitamente
        # a lo mejor está cargando los resultados
        return self.imágenes_cargadas(navegador)


class Buscador:
    """Abrir url de solotodo haciéndole el quite a sus mañas

    Principalmente basado en {}""".format(
            "https://medium.com"
            "/the-andela-way/"
            "introduction-to-web-scraping-using-selenium-7ec377a8cf72"
            )

    def __init__(self,
                 avisarVacíos=False):
        """Crea instancia para múltiples consultas

        """
        self.avisarVacíos = avisarVacíos
        self.__conexión_navegador = None

    def filtrar_basura(self, consulta, resultados):
        '''solotodo separa automáticamente las palabras separadas por ⎡-⎦

        si busco "holi-chai", busca por "holi" y "chai" separadamente.
        Asumiendo que los monitores tienen un nombre importante antes del
        ⎡-⎦, saco las urls que _no_ tengan este nombre importante'''
        if '-' not in consulta:
            # nada que filtrar
            return resultados
        nombre_clave = consulta.split('-')[0]
        correctos = [url for url in resultados
                     if nombre_clave in url]
        return correctos

    def buscar(self, consulta):
        '''Buscar en http://www.solotodo.com/
        '''
        self._abrir("https://www.solotodo.com/search?search={}".format(
            consulta))
        elementos = (
                    self.navegador
                    .find_elements_by_xpath(
                        "//div[@class='price flex-grow']/a"))
        resultados = [e.get_attribute('href') for e in elementos]

        if not resultados and self.avisarVacíos:
            warnings.warn("Sin resultados")
        resultadosÚnicos = list(set(resultados))
        return self.filtrar_basura(consulta, resultadosÚnicos)

    def _abrir(self, url):
        '''Cargar url en navegador (para ser leída después)'''
        self.navegador.get(url)
        tiempo_max = 10000
        try:
            # esperar hasta que estén cargadas…
            (WebDriverWait(self.navegador, tiempo_max)
                .until(resultados_listos(
                    (By.XPATH,
                        # … las imágenes de los productos
                        "//div[@class='image-container d-flex flex-column justify-content-center']/a/img"))))

        except TimeoutException as e:
            self.navegador.quit()
            raise RuntimeError("Tiempo máximo excedido") from e

    def obtener_navegador(self):
        opciones = webdriver.firefox.options.Options()
        opciones.add_argument("--private-window")
        navegador = webdriver.Firefox(options=opciones)
        return navegador

    @property
    def navegador(self):
        if self.__conexión_navegador is None:
            self.__conexión_navegador = self.obtener_navegador()
        return self.__conexión_navegador

    def cerrar_navegador(self):
        if self.__conexión_navegador is not None:
            self.navegador.close()
        self.__conexión_navegador = None


@contextlib.contextmanager
def buscador():
    _buscador = Buscador()
    yield _buscador
    _buscador.cerrar_navegador()
