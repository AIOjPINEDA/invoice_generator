"""
Category matching module for automatic categorization of bank transactions.
"""

# Mapping of keywords to expense categories
EXPENSE_KEYWORDS = {
    # Office expenses
    1: [
        'MATERIAL', 'OFICINA', 'PAPELERIA', 'AMAZON', 'CARTUCHO', 'TINTA',
        'IMPRESORA', 'PAPEL', 'CARPETA', 'ARCHIVADOR'
    ],
    
    # Transportation
    2: [
        'TAXI', 'CABIFY', 'UBER', 'RENFE', 'METRO', 'BUS', 'AUTOBUS',
        'TRANSPORTE', 'GASOLINA', 'COMBUSTIBLE', 'PARKING', 'APARCAMIENTO',
        'PEAJE', 'AUTOPISTA', 'TALLER', 'COCHE', 'VEHICULO', 'ITV'
    ],
    
    # Food
    3: [
        'RESTAURANTE', 'CAFETERIA', 'BAR', 'COMIDA', 'CAFE', 'MENU',
        'DESAYUNO', 'ALMUERZO', 'CENA', 'MERCADONA', 'CARREFOUR', 'LIDL',
        'SUPERMERCADO', 'ALIMENTACION'
    ],
    
    # Professional services
    4: [
        'ASESORIA', 'CONSULTORIA', 'ABOGADO', 'NOTARIO', 'GESTOR',
        'CONTABLE', 'FISCAL', 'LEGAL', 'SERVICIO PROFESIONAL'
    ],
    
    # Social Security
    5: [
        'SEGURIDAD SOCIAL', 'AUTONOMO', 'CUOTA', 'TGSS', 'COTIZACION'
    ],
    
    # Health insurance
    6: [
        'SEGURO MEDICO', 'ADESLAS', 'SANITAS', 'ASISA', 'DKV', 'MAPFRE SALUD',
        'SEGURO SALUD', 'MUTUA', 'FARMACIA', 'MEDICO', 'CLINICA', 'HOSPITAL'
    ],
    
    # Utilities
    7: [
        'LUZ', 'ELECTRICIDAD', 'ENDESA', 'IBERDROLA', 'NATURGY', 'GAS',
        'AGUA', 'CANAL', 'TELEFONO', 'MOVIL', 'INTERNET', 'FIBRA',
        'MOVISTAR', 'VODAFONE', 'ORANGE', 'JAZZTEL', 'MASMOVIL', 'YOIGO'
    ],
    
    # Equipment
    8: [
        'ORDENADOR', 'PORTATIL', 'LAPTOP', 'TABLET', 'MOVIL', 'SMARTPHONE',
        'MONITOR', 'TECLADO', 'RATON', 'IMPRESORA', 'ESCANER', 'DISCO',
        'MEMORIA', 'USB', 'HARDWARE', 'SOFTWARE', 'LICENCIA', 'APPLE',
        'MICROSOFT', 'DELL', 'HP', 'LENOVO', 'ASUS', 'ACER', 'SAMSUNG'
    ],
    
    # Training
    9: [
        'CURSO', 'FORMACION', 'LIBRO', 'EBOOK', 'SEMINARIO', 'CONFERENCIA',
        'CONGRESO', 'TALLER', 'WEBINAR', 'ACADEMIA', 'UNIVERSIDAD', 'MASTER',
        'CERTIFICACION', 'UDEMY', 'COURSERA', 'EDUCACION'
    ]
}

# Mapping of keywords to income sources
INCOME_KEYWORDS = {
    # Invoices
    1: [
        'FACTURA', 'HONORARIO', 'SERVICIO', 'CLIENTE', 'PROYECTO',
        'CONSULTOR', 'DESARROLLO', 'ARTIFICIAL', 'INTELLIGENCE', 'ORCHESTRATOR',
        'AIO', 'GUADALIX', 'AYUNTAMIENTO'
    ],
    
    # Tax refunds
    2: [
        'DEVOLUCION', 'HACIENDA', 'AEAT', 'AGENCIA TRIBUTARIA', 'IRPF',
        'IVA', 'IMPUESTO'
    ],
    
    # Grants
    3: [
        'SUBVENCION', 'AYUDA', 'BECA', 'GRANT', 'FONDO', 'PROGRAMA'
    ]
}

def match_expense_category(description):
    """
    Match a transaction description to an expense category.
    
    Args:
        description (str): The transaction description
        
    Returns:
        int: The category ID, or 10 (Others) if no match is found
    """
    if not description:
        return 10  # Default to "Others"
    
    # Convert to uppercase for case-insensitive matching
    upper_desc = description.upper()
    
    # Check each category's keywords
    for category_id, keywords in EXPENSE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in upper_desc:
                return category_id
    
    # Default to "Others" (category_id = 10)
    return 10

def match_income_source(description):
    """
    Match a transaction description to an income source.
    
    Args:
        description (str): The transaction description
        
    Returns:
        int: The source ID, or 4 (Others) if no match is found
    """
    if not description:
        return 4  # Default to "Others"
    
    # Convert to uppercase for case-insensitive matching
    upper_desc = description.upper()
    
    # Check each source's keywords
    for source_id, keywords in INCOME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in upper_desc:
                return source_id
    
    # Default to "Others" (source_id = 4)
    return 4
