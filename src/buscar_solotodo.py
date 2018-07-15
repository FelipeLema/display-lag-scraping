# -*- coding: utf-8 -*-
''' Buscar en http://www.solotodo.com/
'''
from math import ceil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import datetime
import time
import warnings


class Buscador:
    """Abrir url de solotodo haciéndole el quite a sus mañas

    Principalmente basado en {}""".format(
            "https://medium.com"
            "/the-andela-way/"
            "introduction-to-web-scraping-using-selenium-7ec377a8cf72"
            )

    def __init__(self,
                 descanso=datetime.timedelta(seconds=60),
                 avisarVacíos=False):
        """Crea instancia para múltiples consultas

        """
        self.descanso = descanso
        self.avisarVacíos = avisarVacíos
        self.__conexión_navegador = None

    def buscar(self, consulta):
        '''Buscar en http://www.solotodo.com/
        '''
        self.navegador.get("https://www.solotodo.com/search?search={}".format(consulta))
        elementos = (
                    self.navegador
                    .find_elements_by_xpath(
                        "//div[@class='price flex-grow']/a"))
        import pudb; pu.db
        print([e for e in elementos])
        print(dir(elementos[0]))
        resultados = [e.get_attribute('href') for e in elementos]

        if not resultados and self.avisarVacíos:
            warnings.warn("Sin resultados")
        resultadosÚnicos = list(set(resultados))
        urlsCompletas = list(map(lambda url: "http://www.solotodo.com"+url,
                                 resultadosÚnicos))

        # Al parececer, solotodo no deja buscar de corrido
        time.sleep(ceil(self.descanso.total_seconds()))

        return urlsCompletas

    def _abrir(self, url):
        '''Cargar url en navegador (para ser leída después)'''
        self.navegador.get(url)
        tiempo_max = 10000
        try:
            (WebDriverWait(self.navegador, tiempo_max)
                .until(EC.visibility_of_element_located(
                    (By.XPATH,
                        "//div[@class='{}']".format(
                            "d-flex flex-column category-browse-result"
                            )))))

        except TimeoutException as e:
            self.navegador.quit()
            raise RuntimeError("Tiempo máximo excedido") from e

    def obtener_navegador(self):
        opciones = webdriver.firefox.options.Options()
        opciones.add_argument("--private-window")
        return webdriver.Firefox(options=opciones)

    @property
    def navegador(self):
        if self.__conexión_navegador is None:
            self.__conexión_navegador = self.obtener_navegador()
        return self.__conexión_navegador

    def cerrar_navegador(self):
        if self.__conexión_navegador is not None:
            self.navegador.close()
        self.__conexión_navegador = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cerrar_navegador()
        return self
