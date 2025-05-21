# 📺 M3U Processor: Optimizador y Organizador de Listas IPTV

¡Bienvenido al **M3U Processor**! Este potente script de Python ha sido cuidadosamente diseñado para transformar tus listas de canales IPTV (archivos M3U) de un simple listado a una experiencia de visualización fluida, organizada y siempre actualizada. Olvídate de los canales que no funcionan, la programación desfasada o las listas desordenadas. Con esta herramienta, tendrás el control total sobre tu contenido multimedia.

---

## ✨ Características Principales

El M3U Processor no es solo un verificador de enlaces; es una solución integral para la gestión de tus listas IPTV.

* **Verificación de Conectividad de Canales:**
    * **¿Qué hace?** Recorre cada URL de streaming en tu archivo M3U y realiza una comprobación activa para determinar si el canal está en línea y responde correctamente.
    * **Beneficio:** Elimina la frustración de intentar ver canales que ya no están activos. El script identifica y te informa sobre los canales fallidos, permitiéndote generar una lista final libre de enlaces rotos.
    * **Control:** Puedes definir un tiempo de espera (`timeout`) para las conexiones, ajustándolo a la velocidad de tu red.

* **Asignación Inteligente de EPG (Guía de Programación Electrónica):**
    * **¿Qué hace?** Se conecta a una URL de guía EPG en formato XMLTV (como la proporcionada por `davidmuma/EPG_dobleM`) y, de forma avanzada, empareja los nombres de tus canales M3U con los identificadores (`tvg-id`) de la guía EPG.
    * **Tecnología:** Utiliza la librería `fuzzywuzzy` para realizar **coincidencia difusa (fuzzy matching)**. Esto significa que incluso si los nombres de tus canales en el M3U no coinciden exactamente con los de la EPG (ej., "LaLiga" vs. "La Liga", "Movistar Plus+" vs. "M+ Plus"), el script encontrará la mejor correspondencia posible.
    * **Beneficio:** Asegura que tu reproductor multimedia (Jellyfin, Kodi, VLC, etc.) muestre siempre la información de programación correcta, los logos de los canales y los detalles de los programas.

* **Numeración y Ordenación Lógica de Canales (`tvg-chno`):**
    * **¿Qué hace?** Asigna números de canal (`tvg-chno`) a cada entrada de tu lista M3U, lo que permite a tu reproductor ordenar los canales de forma numérica.
    * **Inteligencia Española:** Incluye una configuración predefinida (`COMMON_SPANISH_CHANNELS_ORDER`) que prioriza y asigna números familiares a los canales españoles más comunes (La 1, Antena 3, Telecinco, etc.).
    * **Flexibilidad:** Los canales no incluidos en la lista de prioritarios se numeran secuencialmente a partir de un número inicial que puedes definir.
    * **Beneficio:** Proporciona una experiencia de navegación similar a la televisión tradicional, con canales ordenados de forma intuitiva.

* **Gestión Avanzada de Canales Duplicados:**
    * **¿Qué hace?** Aborda el problema común de tener el mismo canal listado varias veces en diferentes calidades (ej., "Canal X HD", "Canal X SD", "Canal X FHD").
    * **Opciones configurables:**
        * `Mantener todos`: Incluye todas las versiones del canal que funcionen.
        * `Priorizar calidad`: Analiza el nombre del canal para detectar palabras clave como "UHD", "FHD", "HD", "SD" y selecciona automáticamente la versión de mayor calidad disponible. Si hay varias de la misma calidad, mantiene la primera encontrada.
        * `Mantener el primero`: Simplemente toma la primera aparición del canal en el archivo M3U y descarta las subsiguientes.
    * **Beneficio:** Permite generar una lista M3U más concisa y sin redundancias, optimizando el rendimiento de tu reproductor y la claridad de tu lista de canales.

* **Generación de Lista Limpia y Optimizada:**
    * **¿Qué hace?** El script puede generar un **nuevo archivo M3U** con todos los canales válidos, correctamente asociados a su EPG y numerados según tus preferencias.
    * **Alternativa:** También ofrece la opción de modificar directamente el archivo M3U de entrada, eliminando los canales que no funcionan.
    * **Beneficio:** Asegura que tu lista final sea eficiente, funcional y fácil de usar, sin enlaces rotos ni desorden.

* **Interfaz de Usuario Amigable y Visualmente Atractiva:**
    * **¿Qué hace?** Presenta un menú interactivo en la consola con un diseño mejorado, utilizando colores y caracteres especiales para una experiencia visual más agradable.
    * **Beneficio:** Facilita la configuración de todas las opciones del script, haciéndolo accesible incluso para usuarios con poca experiencia en línea de comandos.

* **Manejo Robusto de Interrupciones:**
    * **¿Qué hace?** Si necesitas detener el proceso de comprobación de canales (ej., presionando `Ctrl+C`), el script te preguntará si deseas continuar con la asignación de EPG/numeración para los canales ya verificados o si prefieres salir completamente.
    * **Beneficio:** Te da control durante ejecuciones largas, permitiéndote guardar el progreso parcial si es necesario.

---

## 🛠️ Dependencias

Para que el M3U Processor funcione sin problemas en tu sistema, necesitas tener **Python 3.x** instalado. Además, el script utiliza varias librerías de Python que no vienen preinstaladas por defecto.

### Instalación de Python

Si aún no tienes Python 3.x en tu sistema, te recomendamos descargarlo desde el sitio web oficial. Asegúrate de seleccionar la versión adecuada para tu sistema operativo (Windows, macOS, Linux) y de marcar la opción "Add Python to PATH" durante la instalación en Windows para facilitar su uso desde la terminal.

* **Descarga Python:** [https://www.python.org/downloads/](https://www.python.org/downloads/)

### Instalación de Librerías Necesarias

Una vez que Python esté instalado, abre tu terminal (o Símbolo del Sistema en Windows, o Terminal en macOS/Linux) y ejecuta los siguientes comandos. `pip` es el gestor de paquetes de Python y se encargará de descargar e instalar estas librerías.

```bash
pip install requests
pip install tqdm
pip install fuzzywuzzy
pip install python-Levenshtein # Opcional, pero muy recomendado para un mejor rendimiento de fuzzywuzzy
```

* **`requests`**: Es una librería esencial para realizar solicitudes HTTP. El script la utiliza para descargar la guía EPG desde la web y para comprobar si las URLs de los canales están activas y responden correctamente.

* **`tqdm`**: Proporciona barras de progreso inteligentes y rápidas para bucles. La verás en acción cuando el script esté comprobando un gran número de canales, dándote una indicación visual del progreso.

* **`fuzzywuzzy`**: Una librería de coincidencia de cadenas que implementa algoritmos de distancia de Levenshtein. Es fundamental para la "inteligencia" del script al emparejar nombres de canales M3U con nombres de EPG que pueden tener pequeñas diferencias o variaciones.

* **`python-Levenshtein`**: Es una implementación en C del algoritmo de Levenshtein. Si la instalas, `fuzzywuzzy` la detectará automáticamente y la usará para realizar las comparaciones de cadenas de forma mucho más rápida y eficiente. Es opcional, pero si vas a procesar listas grandes, notarás la diferencia en la velocidad.

## 🚀 Cómo Usar el Script

Una vez que hayas completado la instalación de Python y todas las dependencias, estás listo para usar el M3U Processor.

1.  **Descarga el Script:**
    * Asegúrate de tener el archivo del script (por ejemplo, `m3u_processor.py`) guardado en una carpeta de tu ordenador. Puedes descargarlo directamente desde este repositorio de GitHub.

2.  **Abre tu Terminal:**
    * Es crucial que abras tu terminal o línea de comandos y navegues hasta la carpeta donde guardaste `m3u_processor.py`. Utiliza el comando `cd` (change directory):

        ```bash
        # Ejemplo en Windows
        cd C:\Users\TuUsuario\Documentos\M3U_Processor

        # Ejemplo en macOS/Linux
        cd /Users/TuUsuario/Documents/M3U_Processor
        ```

        (Reemplaza la ruta con la ubicación real en tu sistema).

3.  **Inicia el Script:**
    * Una vez en la carpeta correcta, simplemente ejecuta el script sin ningún argumento.

    ```bash
    python m3u_processor.py
    ```

4.  **Navega por el Menú Interactivo:**
    * El script te presentará un menú en la consola con un diseño visualmente atractivo. Sigue las instrucciones y selecciona las opciones que desees configurar para tu procesamiento.

    ```
    ╔═════════════════════════════════════════════════════════╗
    ║          M3U PROCESSOR - Configuración                ║
    ╠═════════════════════════════════════════════════════════╣
    ║ 1. Archivo M3U de entrada: NO ESPECIFICADO              ║
    ║ 2. Tiempo de espera (segundos): 5                       ║
    ║ 3. Nombre del archivo M3U de salida: Modificar original ║
    ║ 4. Número inicial de canal: 1                           ║
    ║ 5. Borrar canales fallidos automáticamente: No          ║
    ║ 6. Manejo de canales duplicados: Mantener todos         ║
    ╠═════════════════════════════════════════════════════════╣
    ║ 7. Iniciar procesamiento                                ║
    ║ 8. Salir                                                ║
    ╚═════════════════════════════════════════════════════════╝
    Selecciona una opción (1-8):
    ```

    * **1. Archivo M3U de entrada:**
        * Al seleccionar esta opción, el script buscará automáticamente todos los archivos `.m3u` en la carpeta actual y te los listará con un número.
        * Puedes introducir el número del archivo que deseas procesar.
        * Si tu archivo no está en la lista (ej., está en otra ubicación), selecciona `0` para introducir la ruta completa manualmente.
        * *Ejemplo:* `Selecciona un número o '0' para ruta manual: 1` (si tu archivo es el primero de la lista).

    * **2. Tiempo de espera (segundos):**
        * Define el tiempo máximo (en segundos) que el script esperará a que cada URL de canal responda.
        * Un valor más bajo (ej., 3-5 segundos) hará el proceso más rápido, pero podría descartar canales que tardan un poco más en cargar.
        * Un valor más alto (ej., 10-15 segundos) es más tolerante con conexiones lentas, pero el proceso tardará más.
        * *Ejemplo:* `Introduce el tiempo de espera en segundos (ej. 5): 7`

    * **3. Nombre del archivo M3U de salida:**
        * Introduce el nombre que deseas para el nuevo archivo M3U que el script generará con los canales optimizados.
        * Si lo dejas en blanco y presionas `Enter`, el script **modificará el archivo M3U de entrada original**. ¡Ten precaución con esta opción!
        * *Ejemplo:* `Introduce el nombre del nuevo archivo M3U (deja en blanco para modificar el original): mi_lista_final.m3u`

    * **4. Número inicial de canal:**
        * Establece el número desde el cual comenzará la numeración secuencial de los canales que no están en la lista de canales prioritarios.
        * Por defecto es `1`. Puedes usar un número más alto si quieres dejar espacio para otros canales al principio de tu lista.
        * *Ejemplo:* `Introduce el número inicial para los canales (ej. 1): 100`

    * **5. Borrar canales fallidos automáticamente:**
        * Esta opción solo tiene efecto si has decidido **modificar el archivo M3U de entrada original** (dejando la Opción 3 en blanco).
        * Si seleccionas `s` (sí), los canales que no funcionen se eliminarán del archivo original sin pedir confirmación adicional.
        * Si seleccionas `n` (no), se te preguntará canal por canal si deseas eliminarlos.
        * *Ejemplo:* `¿Borrar automáticamente los canales fallidos? (s/n): s`

    * **6. Manejo de canales duplicados:**
        * Define cómo el script debe tratar las múltiples entradas para el mismo canal (identificadas por su nombre normalizado).
        * **1. Mantener todos los duplicados:** Incluirá todas las versiones del canal que funcionen.
        * **2. Priorizar calidad (UHD > FHD > HD > SD):** El script intentará seleccionar la versión de mayor calidad disponible. Si hay varias de la misma calidad, mantendrá la primera que encuentre.
        * **3. Mantener el primero encontrado:** Incluirá solo la primera aparición del canal en el archivo M3U y descartará las subsiguientes.
        * *Ejemplo:* `Tu elección (1-3): 2`

    * **7. Iniciar procesamiento:**
        * Una vez que todas las opciones estén configuradas a tu gusto, selecciona esta opción para comenzar el análisis.
        * El script mostrará barras de progreso y mensajes de estado durante la comprobación de conexiones y la asignación de EPG/numeración.
        * **Puedes cancelar el proceso** en cualquier momento presionando `Ctrl+C`. El script te preguntará si quieres guardar los resultados parciales o salir.

    * **8. Salir:**
        * Cierra el script de forma segura.

## ⚙️ Configuración del Orden de Canales (`COMMON_SPANISH_CHANNELS_ORDER`)

El script incluye un diccionario Python llamado `COMMON_SPANISH_CHANNELS_ORDER` que define el orden numérico preferido (`tvg-chno`) para una selección de canales españoles comunes. Este diccionario se encuentra directamente en el código fuente del script.

**Puedes editar este diccionario directamente en el archivo `m3u_processor.py`** para personalizar el orden a tu gusto, añadir nuevos canales prioritarios o ajustar los números existentes.

* **Claves del diccionario:** Son los nombres **normalizados** de los canales (en minúsculas, sin espacios extra, y sin sufijos como "HD", "SD", "TV", "Plus+", "720", "1080", "FHD", "UHD"). La función `normalizar_nombre_canal` es la que realiza esta transformación.

* **Valores del diccionario:** Son los números de canal (`tvg-chno`) que deseas asignar a esos canales.

**Ejemplo de personalización en el código:**

```python
COMMON_SPANISH_CHANNELS_ORDER = {
    # Canales nacionales generales
    "la 1": 1,
    "la 2": 2,
    "antena 3": 3,
    "cuatro": 4,
    "telecinco": 5,
    "la sexta": 6,
    "movistar plus": 7,
    "movistar la liga": 20,
    # ... otros canales ya definidos ...

    # Puedes añadir tus propios canales o modificar los existentes:
    "mi canal favorito de cocina": 300, # Asegúrate de que el nombre esté normalizado
    "canal de series premium": 301,
    "deportes extra": 500,
}
```

**Consideraciones al personalizar:**

* Asegúrate de que las claves del diccionario (`"mi canal favorito de cocina"`) sean la versión normalizada del nombre que aparece en tu lista M3U.

* Evita números duplicados en los valores, ya que cada canal solo puede tener un `tvg-chno` asignado por este método.

* Los canales que no estén en este diccionario se numerarán secuencialmente después de los canales prioritarios, a partir del "Número inicial de canal" que configures en el menú.

## 🤝 Contribución

¡Las contribuciones a este proyecto son bienvenidas y muy valoradas! Si tienes ideas para mejorar el script, encuentras un error, o quieres añadir nuevas funcionalidades (como la gestión de `group-title` o la externalización de configuraciones), no dudes en participar.

Para contribuir, sigue el flujo de trabajo estándar de GitHub:

1.  **Haz un "Fork" del Repositorio:** Crea una copia del repositorio en tu propia cuenta de GitHub.

2.  **Clona tu "Fork" Localmente:** Descarga tu copia del repositorio a tu máquina.

    ```bash
    git clone [https://github.com/tu_usuario/M3U-Processor.git](https://github.com/tu_usuario/M3U-Processor.git)
    cd M3U-Processor
    ```

3.  **Crea una Nueva Rama:** Trabaja en una rama separada para tus cambios. Dale un nombre descriptivo (ej., `feature/añadir-group-title`, `bugfix/error-timeout`).

    ```bash
    git checkout -b feature/nueva-funcionalidad
    ```

4.  **Realiza tus Cambios:** Edita el código, añade nuevas funciones, corrige errores, etc.

5.  **Haz "Commit" de tus Cambios:** Guarda tus cambios en tu rama local con un mensaje claro y conciso.

    ```bash
    git add .
    git commit -m 'Añadida nueva funcionalidad X: [Descripción breve]'
    ```

6.  **Haz "Push" a tu Rama:** Sube tus cambios a tu repositorio "fork" en GitHub.

    ```bash
    git push origin feature/nueva-funcionalidad
    ```

7.  **Abre un "Pull Request" (PR):** Desde tu repositorio "fork" en GitHub, verás una opción para abrir un "Pull Request" a la rama `main` del repositorio original. Explica detalladamente los cambios que has realizado y por qué son beneficiosos.

## 📄 Licencia

Este proyecto está distribuido bajo la **Licencia MIT**. Esto significa que eres libre de usar, modificar y distribuir este software, siempre y cuando incluyas la atribución original de la licencia.

Consulta el archivo `LICENSE` en el repositorio para obtener el texto completo de la licencia.

## ✉️ Contacto

Si tienes preguntas, sugerencias, encuentras algún problema o simplemente quieres saludar, no dudes en contactar al autor del proyecto a través de:

* **GitHub:** [https://github.com/rodillo69](https://github.com/rodillo69)

¡Gracias por usar y contribuir al M3U Processor!
