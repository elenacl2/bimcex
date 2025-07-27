import xml.etree.ElementTree as ET

def calcular_area_poligono(puntos):
    n = len(puntos)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += puntos[i][0] * puntos[j][1]
        area -= puntos[j][0] * puntos[i][1]
    return abs(area) / 2.0

def leer_gbxml(ruta_archivo):
    tree = ET.parse(ruta_archivo)
    root = tree.getroot()
    ns = {'gb': 'http://www.gbxml.org/schema'}

    # Leer materiales con densidades
    materiales = {}
    for mat in root.findall('.//gb:Material', ns):
        id_mat = mat.attrib.get('id')
        density_elem = mat.find('gb:Density', ns)
        density = float(density_elem.text) if density_elem is not None else None
        materiales[id_mat] = {'densidad': density}

    # Leer construcciones con capas
    construcciones = {}
    for cons in root.findall('.//gb:Construction', ns):
        id_cons = cons.attrib.get('id')
        capas = []
        for layer in cons.findall('gb:Layer', ns):
            material_ref = layer.attrib.get('layerIdRef')
            thickness_elem = layer.find('gb:Thickness', ns)
            espesor = float(thickness_elem.text) if thickness_elem is not None else None
            densidad = materiales.get(material_ref, {}).get('densidad')
            if espesor is not None and densidad is not None:
                capas.append(espesor * densidad)
        massa_m2 = sum(capas) if capas else None
        construcciones[id_cons] = {'massa_m2': massa_m2}

    espacios = []
    for espacio in root.findall('.//gb:Space', ns):
        id_espacio = espacio.attrib.get('id')
        nombre = espacio.find('gb:Name', ns)
        nombre = nombre.text if nombre is not None else "Sin nombre"
        espacios.append({'id': id_espacio, 'nombre': nombre})

    superficies = []
    for superficie in root.findall('.//gb:Surface', ns):
        tipo = superficie.attrib.get('surfaceType')
        construccion_id = superficie.attrib.get('constructionIdRef', None)
        area = None
        azimuth = None
        tilt = None

        # Geometría
        planargeometry = superficie.find('gb:PlanarGeometry', ns)
        if planargeometry is not None:
            polylines = planargeometry.findall('gb:PolyLoop/gb:CartesianPoint', ns)
            puntos = []
            for point in polylines:
                coords = point.findall('gb:Coordinate', ns)
                x, y, _ = [float(coord.text) for coord in coords]
                puntos.append((x, y))
            if len(puntos) > 2:
                area = calcular_area_poligono(puntos)
        elif superficie.find('gb:RectangularGeometry', ns) is not None:
            width = superficie.find('gb:RectangularGeometry/gb:Width', ns)
            height = superficie.find('gb:RectangularGeometry/gb:Height', ns)
            if width is not None and height is not None:
                area = float(width.text) * float(height.text)

        # Orientación
        azimuth_elem = superficie.find('gb:Azimuth', ns)
        if azimuth_elem is not None:
            try:
                azimuth = float(azimuth_elem.text)
            except:
                pass

        tilt_elem = superficie.find('gb:Tilt', ns)
        if tilt_elem is not None:
            try:
                tilt = float(tilt_elem.text)
            except:
                pass

        expuesto_al_sol = superficie.attrib.get('exposedToSun', None)
        espacios_adyacentes = [ady.attrib.get('spaceIdRef') for ady in superficie.findall('gb:AdjacentSpaceId', ns)]

        # OPENINGS COMPLETOS
        openings = []
        for opening in superficie.findall('gb:Opening', ns):
            opening_id = opening.attrib.get('id')
            tipo_opening = opening.attrib.get('openingType')
            construccion_opening = opening.attrib.get('constructionIdRef')

            width_elem = opening.find('gb:RectangularGeometry/gb:Width', ns)
            height_elem = opening.find('gb:RectangularGeometry/gb:Height', ns)
            area_opening = None
            if width_elem is not None and height_elem is not None:
                try:
                    area_opening = float(width_elem.text) * float(height_elem.text)
                except:
                    pass

            transmitancia_vidre = None
            if construccion_opening:
                construccion_opening_elem = root.find(f'.//gb:Construction[@id="{construccion_opening}"]', ns)
                if construccion_opening_elem is not None:
                    u_val = construccion_opening_elem.find('gb:U-value', ns)
                    if u_val is not None:
                        try:
                            transmitancia_vidre = float(u_val.text)
                        except:
                            pass

            openings.append({
                'id': opening_id,
                'tipo': tipo_opening,
                'area': area_opening,
                'transmitancia_vidre': transmitancia_vidre
            })

        # Transmitancia global
        transmitancia = None
        if construccion_id:
            construccion_element = root.find(f'.//gb:Construction[@id="{construccion_id}"]', ns)
            if construccion_element is not None:
                u_value_element = construccion_element.find('gb:U-value', ns)
                if u_value_element is not None:
                    try:
                        transmitancia = float(u_value_element.text)
                    except:
                        pass

        massa_m2 = construcciones.get(construccion_id, {}).get('massa_m2')

        superficies.append({
            'tipo': tipo,
            'area': area,
            'azimuth': azimuth,
            'tilt': tilt,
            'expuesto_al_sol': expuesto_al_sol,
            'construccion': construccion_id,
            'transmitancia': transmitancia,
            'massa_m2': massa_m2,
            'espacios_adyacentes': espacios_adyacentes,
            'openings': openings
        })

    # INSTALACIONES
    instalaciones = []
    for sistema in root.findall('.//gb:HVACSystem', ns):
        id_ = sistema.attrib.get('id')
        nombre = sistema.find('gb:Name', ns)
        nombre = nombre.text if nombre is not None else "Sin nombre"
        instalaciones.append({'tipo': 'HVAC', 'id': id_, 'nombre': nombre})

    for equipo in root.findall('.//gb:HeatingSystem', ns):
        instalaciones.append({'tipo': 'Calefacción', 'id': equipo.attrib.get('id'),
                              'nombre': equipo.findtext('gb:Name', default='Sin nombre', namespaces=ns)})

    for equipo in root.findall('.//gb:CoolingSystem', ns):
        instalaciones.append({'tipo': 'Refrigeración', 'id': equipo.attrib.get('id'),
                              'nombre': equipo.findtext('gb:Name', default='Sin nombre', namespaces=ns)})

    for luz in root.findall('.//gb:LightingSystem', ns):
        instalaciones.append({'tipo': 'Iluminación', 'id': luz.attrib.get('id'),
                              'nombre': luz.findtext('gb:Name', default='Sin nombre', namespaces=ns)})

    return espacios, superficies, instalaciones



