import requests
import sys
import os
import re
from tqdm import tqdm
import xml.etree.ElementTree as ET
from fuzzywuzzy import fuzz

# Referencia del desarrollador/usuario
# GitHub: https://github.com/rodillo69

class Colors:
    RESET = '\033[0m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

EPG_GUIDE_URL = "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml"

COMMON_SPANISH_CHANNELS_ORDER = {
    "la 1": 1,
    "la 2": 2,
    "antena 3": 3,
    "cuatro": 4,
    "telecinco": 5,
    "la sexta": 6,
    "movistar plus": 7,
    "movistar plus+": 7,
    "movistar estrenos": 8,
    "movistar estrenos 2": 9,
    "movistar cine": 10,
    "movistar series": 11,
    "movistar series 2": 12,
    "movistar comedia": 13,
    "movistar drama": 14,
    "movistar accion": 15,
    "movistar clasicos": 16,
    "movistar festivales": 17,
    "movistar va de cine": 18,
    "movistar la liga": 20,
    "movistar la liga 2": 21,
    "movistar liga de campeones": 22,
    "movistar liga de campeones 2": 23,
    "movistar f1": 24,
    "movistar deportes": 25,
    "movistar deportes 2": 26,
    "movistar golf": 27,
    "movistar toros": 28,
    "movistar vamos": 29,
    "movistar zero": 30,
    "movistar documentales": 31,
    "movistar investigacion": 32,
    "movistar clasica": 33,
    "movistar pop": 34,
    "movistar rock": 35,
    "movistar jazz": 36,
    "movistar hits": 37,
    "movistar cines": 38,
    "movistar seriesmania": 39,
    "atreseries": 40,
    "neox": 41,
    "nova": 42,
    "mega": 43,
    "fdf": 44,
    "energy": 45,
    "divinity": 46,
    "boing": 47,
    "clan": 48,
    "paramount network": 49,
    "dmax": 50,
    "trece": 51,
    "dkiss": 52,
    "gol play": 53,
    "real madrid tv": 54,
    "barca tv": 55,
    "teledeporte": 56,
    "24h": 57,
    "rtve play": 58,
    "sx3": 59,
    "tv3": 60,
    "33": 61,
    "esport3": 62,
    "super3": 63,
    "8tv": 64,
    "telemadrid": 70,
    "la otra": 71,
    "canal sur": 80,
    "canal sur 2": 81,
    "etb1": 90,
    "etb2": 91,
    "etb3": 92,
    "etb4": 93,
    "tvg": 100,
    "tvg2": 101,
    "apunt": 110,
    "apunt esports": 111,
    "aragontv": 120,
    "rtpa": 130,
    "canal extremadura": 140,
    "la 7 tv murcia": 150,
    "ib3": 160,
    "rtvc": 170,
    "rtvcm": 180,
    "cyld": 190,
    "la rioja tv": 200,
    "navarra tv": 210,
    "castilla la mancha media": 220,
    "cyl7": 230,
    "cyl8": 231,
}

def comprobar_conexion(url, timeout=5):
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        return 200 <= response.status_code < 300
    except requests.exceptions.RequestException:
        return False

def leer_m3u(archivo_m3u):
    lineas = []
    try:
        with open(archivo_m3u, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print(f"{Colors.RED}{Colors.BOLD}Error:{Colors.RESET} El archivo '{archivo_m3u}' no se encontró.")
        sys.exit(1)
    return lineas

def normalizar_nombre_canal(nombre):
    nombre = nombre.lower()
    nombre = re.sub(r'\s*(hd|sd|fhd|uhd|720|1080|tv|plus\+)\s*', '', nombre)
    nombre = re.sub(r'[^a-z0-9\s]', '', nombre)
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    return nombre

def descargar_y_parsear_epg(url_epg, timeout=10):
    epg_data = {}
    print(f"\n{Colors.YELLOW}Descargando y parseando la guía EPG desde: {Colors.BOLD}{url_epg}{Colors.RESET}")
    try:
        response = requests.get(url_epg, timeout=timeout)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        for channel_elem in root.findall('channel'):
            channel_id = channel_elem.get('id')
            if channel_id:
                normalized_channel_id = normalizar_nombre_canal(channel_id)
                if normalized_channel_id not in epg_data:
                    epg_data[normalized_channel_id] = channel_id
                
                for display_name_elem in channel_elem.findall('display-name'):
                    display_name = display_name_elem.text
                    if display_name:
                        normalized_display_name = normalizar_nombre_canal(display_name)
                        if normalized_display_name not in epg_data:
                            epg_data[normalized_display_name] = channel_id
        
        print(f"{Colors.GREEN}EPG parseado con éxito. Canales EPG encontrados: {len(set(epg_data.values()))}{Colors.RESET}")
        return epg_data

    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}{Colors.BOLD}Error al descargar EPG:{Colors.RESET} {e}")
        return None
    except ET.ParseError as e:
        print(f"{Colors.RED}{Colors.BOLD}Error al parsear EPG XML:{Colors.RESET} {e}")
        return None

def encontrar_epg_id(tvg_name_m3u, epg_data):
    normalized_tvg_name = normalizar_nombre_canal(tvg_name_m3u)
    
    if normalized_tvg_name in epg_data:
        return epg_data[normalized_tvg_name]

    best_match_epg_id = None
    highest_score = 0
    
    for epg_normalized_name, epg_id in epg_data.items():
        score = fuzz.token_set_ratio(normalized_tvg_name, epg_normalized_name)
        
        if score > 75 and score > highest_score:
            highest_score = score
            best_match_epg_id = epg_id
        
    return best_match_epg_id

def actualizar_linea_extinf(linea_extinf, nuevo_tvg_id=None, nuevo_tvg_chno=None):
    match = re.match(r'(#EXTINF:[-]?\d+)(.*?)(,.*)', linea_extinf)
    if not match:
        return linea_extinf

    prefix = match.group(1)
    current_attrs_str = match.group(2)
    suffix = match.group(3)

    current_attrs = {}
    for attr_match in re.finditer(r'(\w+?)="([^"]*)"', current_attrs_str):
        current_attrs[attr_match.group(1)] = attr_match.group(2)

    if nuevo_tvg_id is not None:
        current_attrs['tvg-id'] = nuevo_tvg_id

    if nuevo_tvg_chno is not None:
        current_attrs['tvg-chno'] = str(nuevo_tvg_chno)

    new_attrs_list = []
    if 'tvg-id' in current_attrs:
        new_attrs_list.append(f'tvg-id="{current_attrs.pop("tvg-id")}"')
    if 'tvg-chno' in current_attrs:
        new_attrs_list.append(f'tvg-chno="{current_attrs.pop("tvg-chno")}"')
    
    for key, value in sorted(current_attrs.items()):
        new_attrs_list.append(f'{key}="{value}"')
    
    new_attrs_str = ' '.join(new_attrs_list)
    if new_attrs_str:
        new_attrs_str = ' ' + new_attrs_str

    return f"{prefix}{new_attrs_str}{suffix}\n"

def get_quality_score(channel_name):
    name_lower = channel_name.lower()
    if 'uhd' in name_lower:
        return 4
    if 'fhd' in name_lower:
        return 3
    if 'hd' in name_lower:
        return 2
    if 'sd' in name_lower:
        return 1
    return 0

def filter_duplicate_channels(valid_entries, duplicate_handling_method):
    if duplicate_handling_method == 'all':
        return valid_entries

    grouped_channels = {}
    for entry in valid_entries:
        normalized_name = entry['normalized_tvg_name']
        if normalized_name not in grouped_channels:
            grouped_channels[normalized_name] = []
        grouped_channels[normalized_name].append(entry)

    filtered_entries = []
    for normalized_name, channels_list in grouped_channels.items():
        if len(channels_list) == 1:
            filtered_entries.append(channels_list[0])
            continue

        if duplicate_handling_method == 'first':
            filtered_entries.append(channels_list[0])
        elif duplicate_handling_method == 'quality':
            best_quality_channels = []
            max_quality_score = -1
            
            for channel_data in channels_list:
                score = get_quality_score(channel_data['tvg_name'])
                if score > max_quality_score:
                    max_quality_score = score
                    best_quality_channels = [channel_data]
                elif score == max_quality_score:
                    best_quality_channels.append(channel_data)
            
            if best_quality_channels:
                filtered_entries.append(best_quality_channels[0])
        else:
            filtered_entries.extend(channels_list)

    return filtered_entries


def procesar_m3u(archivo_m3u, lineas, borrar_automatico=False, timeout=5, epg_data=None, output_file_name=None, start_channel_number=1, duplicate_handling_method='all'):
    canales_fallidos = []
    valid_channel_entries = []
    non_channel_lines = []

    print(f"\n{Colors.BOLD}Realizando la primera pasada: identificando canales y comprobando conexiones (Timeout: {timeout}s):{Colors.RESET}")
    
    total_channels_to_check = 0
    for i in range(len(lineas)):
        if lineas[i].strip().startswith("#EXTINF:") and i + 1 < len(lineas) and lineas[i+1].strip().startswith("http"):
            total_channels_to_check += 1

    try:
        with tqdm(total=total_channels_to_check, desc="Progreso de conexión", unit="canal") as pbar:
            i = 0
            while i < len(lineas):
                linea_actual = lineas[i].strip()
                
                if linea_actual.startswith("#EXTINF:") and i + 1 < len(lineas):
                    linea_extinf_original = lineas[i]
                    posible_url = lineas[i + 1].strip()

                    if posible_url.startswith("http"):
                        url = posible_url
                        
                        tvg_name_match = re.search(r'tvg-name="([^"]*)"', linea_actual)
                        nombre_canal_m3u = tvg_name_match.group(1).strip() if tvg_name_match else linea_actual.split(',', 1)[-1].strip()
                        
                        pbar.set_description(f"Comprobando: {nombre_canal_m3u}")

                        if comprobar_conexion(url, timeout=timeout):
                            pbar.write(f"Comprobando: {Colors.BOLD}{nombre_canal_m3u}{Colors.RESET} ({url}) ... {Colors.GREEN}OK{Colors.RESET}")
                            valid_channel_entries.append({
                                'extinf_line': linea_extinf_original,
                                'url_line': lineas[i + 1],
                                'tvg_name': nombre_canal_m3u,
                                'normalized_tvg_name': normalizar_nombre_canal(nombre_canal_m3u),
                                'epg_id': None,
                                'processed': False
                            })
                        else:
                            pbar.write(f"Comprobando: {Colors.BOLD}{nombre_canal_m3u}{Colors.RESET} ({url}) ... {Colors.RED}FALLO{Colors.RESET}")
                            canales_fallidos.append((nombre_canal_m3u, url))
                        
                        pbar.update(1)
                        i += 2
                        continue
                
                if not linea_actual.startswith("#EXTM3U"): 
                    non_channel_lines.append(lineas[i])
                i += 1
    except KeyboardInterrupt:
        pbar.close()
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Proceso de comprobación de canales interrumpido por el usuario.{Colors.RESET}")
        respuesta_continuar = input(f"{Colors.BOLD}¿Deseas continuar con la asignación de EPG/numeración y guardar los canales ya comprobados? (s/n): {Colors.RESET}").lower()
        if respuesta_continuar != 's':
            print(f"{Colors.YELLOW}Operación cancelada. No se guardarán cambios.{Colors.RESET}")
            sys.exit(0)

    print(f"\n{Colors.BOLD}Aplicando el método de manejo de duplicados: '{duplicate_handling_method}'...{Colors.RESET}")
    filtered_valid_channel_entries = filter_duplicate_channels(valid_channel_entries, duplicate_handling_method)
    print(f"{Colors.BLUE}Canales válidos después del filtrado de duplicados: {len(filtered_valid_channel_entries)}{Colors.RESET}")

    canales_ok = len(filtered_valid_channel_entries)
    total_canales = canales_ok + len(canales_fallidos)

    final_output_channels_data = []
    assigned_channel_numbers = set()
    canales_con_epg_id = 0
    canales_con_tvg_chno = 0
    
    print(f"\n{Colors.BOLD}Asignando tvg-id y tvg-chno según el orden lógico...{Colors.RESET}")

    for common_normalized_name, desired_chno in COMMON_SPANISH_CHANNELS_ORDER.items():
        if desired_chno in assigned_channel_numbers:
            continue 

        found_channel_data = None
        found_channel_index = -1
        for idx, channel_data in enumerate(filtered_valid_channel_entries):
            if not channel_data['processed'] and channel_data['normalized_tvg_name'] == common_normalized_name:
                found_channel_data = channel_data
                found_channel_index = idx
                break
        
        if found_channel_data:
            epg_id_encontrado = None
            if epg_data:
                epg_id_encontrado = encontrar_epg_id(found_channel_data['tvg_name'], epg_data)
                if epg_id_encontrado:
                    found_channel_data['epg_id'] = epg_id_encontrado
                    canales_con_epg_id += 1

            updated_extinf_line = actualizar_linea_extinf(
                found_channel_data['extinf_line'], 
                nuevo_tvg_id=found_channel_data['epg_id'], 
                nuevo_tvg_chno=desired_chno
            )
            
            final_output_channels_data.append({
                'chno': desired_chno,
                'extinf_line': updated_extinf_line,
                'url_line': found_channel_data['url_line']
            })
            assigned_channel_numbers.add(desired_chno)
            filtered_valid_channel_entries[found_channel_index]['processed'] = True
            canales_con_tvg_chno += 1
            print(f"  {Colors.BLUE}Asignado (Prioritario):{Colors.RESET} '{found_channel_data['tvg_name']}' -> tvg-chno={desired_chno}")

    current_sequential_number = start_channel_number
    
    while current_sequential_number in assigned_channel_numbers:
        current_sequential_number += 1

    remaining_channels_to_process = [
        channel_data for channel_data in filtered_valid_channel_entries 
        if not channel_data['processed']
    ]

    remaining_channels_to_process.sort(key=lambda x: x['normalized_tvg_name'])

    for channel_data in remaining_channels_to_process:
        while current_sequential_number in assigned_channel_numbers:
            current_sequential_number += 1
        
        if channel_data['epg_id'] is None and epg_data:
            epg_id_encontrado = encontrar_epg_id(channel_data['tvg_name'], epg_data)
            if epg_id_encontrado:
                channel_data['epg_id'] = epg_id_encontrado
                canales_con_epg_id += 1

        updated_extinf_line = actualizar_linea_extinf(
            channel_data['extinf_line'], 
            nuevo_tvg_id=channel_data['epg_id'], 
            nuevo_tvg_chno=current_sequential_number
        )
        
        final_output_channels_data.append({
            'chno': current_sequential_number,
            'extinf_line': updated_extinf_line,
            'url_line': channel_data['url_line']
        })
        assigned_channel_numbers.add(current_sequential_number)
        canales_con_tvg_chno += 1
        print(f"  {Colors.BLUE}Asignado (Secuencial):{Colors.RESET} '{channel_data['tvg_name']}' -> tvg-chno={current_sequential_number}")
        current_sequential_number += 1


    nuevas_lineas = []
    if output_file_name:
        nuevas_lineas.append("#EXTM3U\n")
    else:
        if any(line.strip().startswith("#EXTM3U") for line in lineas):
            nuevas_lineas.append("#EXTM3U\n")

    for line in non_channel_lines:
        nuevas_lineas.append(line)

    for channel_info in sorted(final_output_channels_data, key=lambda x: x['chno']):
        nuevas_lineas.append(channel_info['extinf_line'])
        nuevas_lineas.append(channel_info['url_line'])


    print(f"\n{Colors.BOLD}--- Análisis Completo ---{Colors.RESET}")
    print(f"Canales comprobados: {Colors.YELLOW}{total_canales}{Colors.RESET}")
    print(f"Canales funcionando (después de duplicados): {Colors.GREEN}{canales_ok}{Colors.RESET}")
    print(f"Canales fallidos: {Colors.RED}{len(canales_fallidos)}{Colors.RESET}")
    if epg_data:
        print(f"Canales con tvg-id EPG asignado: {Colors.BLUE}{canales_con_epg_id}{Colors.RESET}")
    print(f"Canales con tvg-chno asignado: {Colors.BLUE}{canales_con_tvg_chno}{Colors.RESET}")


    if canales_fallidos:
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Canales que no funcionan:{Colors.RESET}")
        for nombre, url in canales_fallidos:
            print(f"- {Colors.BOLD}{nombre}{Colors.RESET}: {Colors.YELLOW}{url}{Colors.RESET}")

    if output_file_name:
        try:
            with open(output_file_name, 'w', encoding='utf-8') as f:
                f.writelines(nuevas_lineas)
            print(f"{Colors.GREEN}{Colors.BOLD}Nuevo archivo M3U creado con éxito: {output_file_name}{Colors.RESET}")
            if canales_fallidos:
                print(f"{Colors.YELLOW}Los canales fallidos no se incluyeron en el nuevo archivo.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}{Colors.BOLD}Error al crear el nuevo archivo:{Colors.RESET} {e}")
    else:
        if canales_fallidos or canales_con_epg_id > 0 or canales_con_tvg_chno > 0:
            if borrar_automatico:
                try:
                    with open(archivo_m3u, 'w', encoding='utf-8') as f:
                        f.writelines(nuevas_lineas)
                    print(f"{Colors.GREEN}{Colors.BOLD}Los cambios (canales fallidos eliminados, tvg-id/chno asignados) han sido guardados automáticamente en el archivo original.{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}{Colors.BOLD}Error al escribir en el archivo original:{Colors.RESET} {e}")
            else:
                respuesta = input(f"\n{Colors.BOLD}Se han realizado cambios (asignación de tvg-id/chno y/o eliminación de fallidos). ¿Deseas guardar estos cambios en el archivo .m3u original? (s/n): {Colors.RESET}").lower()
                if respuesta == 's':
                    try:
                        with open(archivo_m3u, 'w', encoding='utf-8') as f:
                            f.writelines(nuevas_lineas)
                        print(f"{Colors.GREEN}{Colors.BOLD}Los cambios han sido guardados en el archivo original.{Colors.RESET}")
                    except Exception as e:
                        print(f"{Colors.RED}{Colors.BOLD}Error al escribir en el archivo original:{Colors.RESET} {e}")
                else:
                    print(f"{Colors.YELLOW}No se realizaron cambios en el archivo original.{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}Todos los canales parecen funcionar y no se realizaron cambios de tvg-id/chno en el archivo original.{Colors.RESET}")

def display_menu():
    options = {
        'timeout': 5,
        'output_file_name': None,
        'start_channel_number': 1,
        'auto_borrar': False,
        'input_m3u_file': None,
        'duplicate_handling': 'all'
    }

    # Diccionario para mapear los valores de 'duplicate_handling' a texto legible
    duplicate_display_names = {
        'all': 'Mantener todos',
        'quality': 'Priorizar calidad',
        'first': 'Mantener el primero'
    }

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        # He eliminado el banner ASCII y he dejado el título simple dentro del recuadro.
        print(f"{Colors.MAGENTA}{Colors.BOLD}╔═════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.MAGENTA}║ {Colors.CYAN}{Colors.BOLD}         M3U PROCESSOR - Configuración         {Colors.RESET} {Colors.MAGENTA}║{Colors.RESET}")
        print(f"{Colors.MAGENTA}╠═════════════════════════════════════════════════════════╣{Colors.RESET}")
        
        print(f"{Colors.MAGENTA}║ {Colors.YELLOW}1.{Colors.RESET} Archivo M3U de entrada: {Colors.BOLD}{options['input_m3u_file'] if options['input_m3u_file'] else 'NO ESPECIFICADO':<30}{Colors.RESET}{Colors.MAGENTA}║{Colors.RESET}")
        print(f"{Colors.MAGENTA}║ {Colors.YELLOW}2.{Colors.RESET} Tiempo de espera (segundos): {Colors.BOLD}{options['timeout']:<30}{Colors.RESET}{Colors.MAGENTA}║{Colors.RESET}")
        print(f"{Colors.MAGENTA}║ {Colors.YELLOW}3.{Colors.RESET} Nombre del archivo M3U de salida: {Colors.BOLD}{options['output_file_name'] if options['output_file_name'] else 'Modificar original':<30}{Colors.RESET}{Colors.MAGENTA}║{Colors.RESET}")
        print(f"{Colors.MAGENTA}║ {Colors.YELLOW}4.{Colors.RESET} Número inicial de canal: {Colors.BOLD}{options['start_channel_number']:<30}{Colors.RESET}{Colors.MAGENTA}║{Colors.RESET}")
        print(f"{Colors.MAGENTA}║ {Colors.YELLOW}5.{Colors.RESET} Borrar canales fallidos automáticamente: {Colors.BOLD}{'Sí' if options['auto_borrar'] else 'No':<20}{Colors.RESET}{Colors.MAGENTA}║{Colors.RESET}")
        print(f"{Colors.MAGENTA}║ {Colors.YELLOW}6.{Colors.RESET} Manejo de canales duplicados: {Colors.BOLD}{duplicate_display_names.get(options['duplicate_handling'], 'Desconocido'):<20}{Colors.RESET}{Colors.MAGENTA}║{Colors.RESET}")
        
        print(f"{Colors.MAGENTA}╠═════════════════════════════════════════════════════════╣{Colors.RESET}")
        print(f"{Colors.MAGENTA}║ {Colors.GREEN}7.{Colors.RESET} {Colors.BOLD}Iniciar procesamiento{Colors.RESET}                                      {Colors.MAGENTA}║{Colors.RESET}")
        print(f"{Colors.RED}8.{Colors.RESET} {Colors.BOLD}Salir{Colors.RESET}                                                      {Colors.MAGENTA}║{Colors.RESET}")
        print(f"{Colors.MAGENTA}╚═════════════════════════════════════════════════════════╝{Colors.RESET}")

        choice = input(f"{Colors.BOLD}Selecciona una opción (1-8): {Colors.RESET}").strip()

        if choice == '1':
            m3u_files = [f for f in os.listdir('.') if f.lower().endswith('.m3u')]
            if m3u_files:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{Colors.MAGENTA}{Colors.BOLD}╔═════════════════════════════════════════════════════════╗{Colors.RESET}")
                print(f"{Colors.MAGENTA}║ {Colors.BLUE}Archivos .m3u encontrados en la carpeta actual:{Colors.RESET} {Colors.MAGENTA}║{Colors.RESET}")
                print(f"{Colors.MAGENTA}╠═════════════════════════════════════════════════════════╣{Colors.RESET}")
                for idx, f_name in enumerate(m3u_files):
                    print(f"{Colors.MAGENTA}║  {Colors.YELLOW}{idx + 1}.{Colors.RESET} {f_name:<52}{Colors.MAGENTA}║{Colors.RESET}")
                print(f"{Colors.MAGENTA}║  {Colors.YELLOW}0.{Colors.RESET} Introducir ruta manualmente (si no está en la lista){Colors.RESET} {Colors.MAGENTA}║{Colors.RESET}")
                print(f"{Colors.MAGENTA}╚═════════════════════════════════════════════════════════╝{Colors.RESET}")
                
                while True:
                    file_choice = input(f"{Colors.YELLOW}Selecciona un número o '0' para ruta manual: {Colors.RESET}").strip()
                    if file_choice == '0':
                        file_path = input(f"{Colors.YELLOW}Introduce la ruta completa al archivo M3U de entrada: {Colors.RESET}").strip()
                        if os.path.exists(file_path) and file_path.lower().endswith('.m3u'):
                            options['input_m3u_file'] = file_path
                            break
                        else:
                            print(f"{Colors.RED}Ruta de archivo no válida o no es un archivo .m3u. Inténtalo de nuevo.{Colors.RESET}")
                    else:
                        try:
                            selected_idx = int(file_choice) - 1
                            if 0 <= selected_idx < len(m3u_files):
                                options['input_m3u_file'] = m3u_files[selected_idx]
                                break
                            else:
                                print(f"{Colors.RED}Número no válido. Inténtalo de nuevo.{Colors.RESET}")
                        except ValueError:
                            print(f"{Colors.RED}Entrada no válida. Por favor, introduce un número o '0'.{Colors.RESET}")
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{Colors.MAGENTA}{Colors.BOLD}╔═════════════════════════════════════════════════════════╗{Colors.RESET}")
                print(f"{Colors.MAGENTA}║ {Colors.YELLOW}No se encontraron archivos .m3u en la carpeta actual.{Colors.RESET} {Colors.MAGENTA}║{Colors.RESET}")
                print(f"{Colors.MAGENTA}╚═════════════════════════════════════════════════════════╝{Colors.RESET}")
                while True:
                    file_path = input(f"{Colors.YELLOW}Introduce la ruta completa al archivo M3U de entrada manualmente: {Colors.RESET}").strip()
                    if os.path.exists(file_path) and file_path.lower().endswith('.m3u'):
                        options['input_m3u_file'] = file_path
                        break
                    else:
                        print(f"{Colors.RED}Ruta de archivo no válida o no es un archivo .m3u. Inténtalo de nuevo.{Colors.RESET}")
            
        elif choice == '2':
            while True:
                try:
                    timeout_str = input(f"{Colors.YELLOW}Introduce el tiempo de espera en segundos (ej. 5): {Colors.RESET}").strip()
                    timeout_val = int(timeout_str)
                    if timeout_val > 0:
                        options['timeout'] = timeout_val
                        break
                    else:
                        print(f"{Colors.RED}El tiempo de espera debe ser un número positivo.{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.RED}Entrada no válida. Por favor, introduce un número entero.{Colors.RESET}")
        
        elif choice == '3':
            output_name = input(f"{Colors.YELLOW}Introduce el nombre del nuevo archivo M3U (deja en blanco para modificar el original): {Colors.RESET}").strip()
            if output_name:
                if not output_name.lower().endswith('.m3u'):
                    output_name += '.m3u'
                options['output_file_name'] = output_name
            else:
                options['output_file_name'] = None
        
        elif choice == '4':
            while True:
                try:
                    start_num_str = input(f"{Colors.YELLOW}Introduce el número inicial para los canales (ej. 1): {Colors.RESET}").strip()
                    start_num_val = int(start_num_str)
                    if start_num_val >= 0:
                        options['start_channel_number'] = start_num_val
                        break
                    else:
                        print(f"{Colors.RED}El número inicial debe ser un número no negativo.{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.RED}Entrada no válida. Por favor, introduce un número entero.{Colors.RESET}")
        
        elif choice == '5':
            auto_delete_choice = input(f"{Colors.YELLOW}¿Borrar automáticamente los canales fallidos? (s/n): {Colors.RESET}").strip().lower()
            options['auto_borrar'] = (auto_delete_choice == 's')

        elif choice == '6':
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Colors.MAGENTA}{Colors.BOLD}╔═════════════════════════════════════════════════════════╗{Colors.RESET}")
            print(f"{Colors.MAGENTA}║ {Colors.BLUE}Selecciona el método de manejo de duplicados:{Colors.RESET} {Colors.MAGENTA}║{Colors.RESET}")
            print(f"{Colors.MAGENTA}╠═════════════════════════════════════════════════════════╣{Colors.RESET}")
            print(f"{Colors.MAGENTA}║  {Colors.YELLOW}1.{Colors.RESET} Mantener todos los duplicados                                {Colors.MAGENTA}║{Colors.RESET}")
            print(f"{Colors.MAGENTA}║  {Colors.YELLOW}2.{Colors.RESET} Priorizar calidad (UHD > FHD > HD > SD)                    {Colors.MAGENTA}║{Colors.RESET}")
            print(f"{Colors.MAGENTA}║  {Colors.YELLOW}3.{Colors.RESET} Mantener el primero encontrado                             {Colors.MAGENTA}║{Colors.RESET}")
            print(f"{Colors.MAGENTA}╚═════════════════════════════════════════════════════════╝{Colors.RESET}")
            while True:
                dup_choice = input(f"{Colors.YELLOW}Tu elección (1-3): {Colors.RESET}").strip()
                if dup_choice == '1':
                    options['duplicate_handling'] = 'all'
                    break
                elif dup_choice == '2':
                    options['duplicate_handling'] = 'quality'
                    break
                elif dup_choice == '3':
                    options['duplicate_handling'] = 'first'
                    break
                else:
                    print(f"{Colors.RED}Opción no válida. Por favor, introduce 1, 2 o 3.{Colors.RESET}")
        
        elif choice == '7':
            if options['input_m3u_file']:
                return options
            else:
                input(f"{Colors.RED}¡Atención! Debes especificar la ruta del archivo M3U de entrada (Opción 1) antes de iniciar. Presiona Enter para continuar...{Colors.RESET}")
        
        elif choice == '8':
            print(f"{Colors.YELLOW}Saliendo del script. ¡Hasta pronto!{Colors.RESET}")
            sys.exit(0)
        
        else:
            input(f"{Colors.RED}Opción no válida. Presiona Enter para continuar...{Colors.RESET}")


if __name__ == "__main__":
    config_options = display_menu()

    archivo_m3u = config_options['input_m3u_file']
    auto_borrar = config_options['auto_borrar']
    timeout = config_options['timeout']
    output_file_name = config_options['output_file_name']
    start_channel_number = config_options['start_channel_number']
    duplicate_handling_method = config_options['duplicate_handling']

    epg_data = descargar_y_parsear_epg(EPG_GUIDE_URL)
    if not epg_data:
        print(f"{Colors.RED}No se pudo cargar la guía EPG. Continuando sin asignación de tvg-id.{Colors.RESET}")

    print(f"{Colors.YELLOW}Leyendo el archivo: {Colors.BOLD}{archivo_m3u}{Colors.RESET}")
    lineas = leer_m3u(archivo_m3u)

    if lineas:
        procesar_m3u(archivo_m3u, lineas, auto_borrar, timeout, epg_data, output_file_name, start_channel_number, duplicate_handling_method)
    else:
        print(f"{Colors.YELLOW}El archivo .m3u está vacío.{Colors.RESET}")
