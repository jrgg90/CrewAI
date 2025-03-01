import warnings
warnings.filterwarnings('ignore')

import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar que las claves API necesarias estén disponibles
required_env_vars = ["OPENAI_API_KEY", "SERPER_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")

os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

from crewai import Agent, Crew, Task
from crewai_tools import (
    ScrapeWebsiteTool,
    SerperDevTool,
    ImageProcessingTool,
    DataVisualizationTool,
    FolderReaderTool,
    MarketDataTool,
    FileWriterTool
)

# Inicialización de herramientas de CrewAI
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
image_tool = ImageProcessingTool()
data_viz_tool = DataVisualizationTool()
folder_tool = FolderReaderTool()
market_tool = MarketDataTool()
file_tool = FileWriterTool()

#FUNCTIONS
def process_url_for_filename(url: str) -> str:
    """
    Extrae el dominio principal de una URL para usarlo en el nombre del archivo.
    Args:
        url (str): URL a procesar
    Returns:
        str: Dominio principal limpio
    Raises:
        ValueError: Si la URL está vacía o mal formada
    """
    if not url:
        raise ValueError("La URL no puede estar vacía")
    
    # Eliminar espacios y convertir a minúsculas
    url = url.strip().lower()
    
    # Eliminar protocolo (http://, https://)
    if '://' in url:
        url = url.split('://')[1]
    
    # Eliminar www. si existe
    if url.startswith('www.'):
        url = url[4:]
    
    # Tomar solo el dominio principal (antes de la primera /)
    if '/' in url:
        url = url.split('/')[0]
    
    # Eliminar caracteres no válidos para nombres de archivo
    url = ''.join(c for c in url if c.isalnum() or c in '.-_')
    
    return url

#AGENTS
# Data Collector Agent
data_collector = Agent(
    role="Data Collector",
    goal="Extraer con precisión datos de screenshots relacionados con investigación de mercado",
    backstory="Eres un especialista en extracción de datos que puede interpretar información visual de Google Market Finder e ITC Trade Map. Tu habilidad para organizar datos estructurados es fundamental para el análisis posterior.",
    allow_delegation=False,
    tools=[image_tool, folder_tool],
    verbose=True
)

# Market Analyst Agent
market_analyst = Agent(
    role="Market Analyst",
    goal="Analizar datos de mercado e identificar tendencias y oportunidades comerciales",
    backstory="Como analista de mercados internacionales, tienes experiencia evaluando datos económicos y de comportamiento online para determinar la viabilidad de nuevos mercados. Tu análisis será crucial para identificar los países con mayor potencial.",
    allow_delegation=True,
    tools=[market_tool],
    verbose=True
)

# Export Strategist Agent
export_strategist = Agent(
    role="Export Strategist",
    goal="Determinar los mejores países para exportación basado en criterios múltiples",
    backstory="Eres un estratega de exportación con amplia experiencia en comercio internacional. Tu especialidad es evaluar factores como aranceles, potencial de exportación, volumen de búsquedas y datos económicos para recomendar los mercados óptimos.",
    allow_delegation=True,
    tools=[market_tool, data_viz_tool],
    verbose=True
)

# Report Generator Agent
report_generator = Agent(
    role="Report Generator",
    goal="Crear un informe estructurado y cohesivo sobre potencial de exportación y guardarlo como archivo Markdown",
    backstory="Especialista en comunicación de datos complejos de manera clara y estructurada. Tu habilidad para sintetizar información y presentarla en formatos accesibles es fundamental para que los stakeholders puedan tomar decisiones informadas. Además, te aseguras de que los reportes sean guardados correctamente para su fácil acceso.",
    allow_delegation=False,
    verbose=True,
    tools=[data_viz_tool, file_tool] 
)

#CREATING TASKS

#1. Extracción de Datos de Screenshots
extract_online_profile_task = Task(
    description=(
        "Revisa todos los screenshots en la carpeta {ecommerce_folder} y extrae específicamente la siguiente información del Online Profile: "
        "1. Monthly searches across categories para cada país "
        "2. Google Ads recommended bid para cada país "
        "3. Active internet population para cada país "
        "Busca screenshots que contengan datos de Google Market Finder. "
        "Organiza la información en formato tabular por país."
    ),
    expected_output=(
        "Tabla estructurada con los tres datos específicos del Online Profile para cada país identificado. "
        "La tabla debe incluir columnas para país, búsquedas mensuales, costo recomendado de Google Ads, "
        "y población activa en internet."
    ),
    tools=[image_tool],
    agent=data_collector
)

extract_economic_profile_task = Task(
    description=(
        "Revisa todos los screenshots en la carpeta {ecommerce_folder} y extrae específicamente la siguiente información del Economic Profile: "
        "1. Population Size para cada país "
        "2. Median Age para cada país "
        "3. GDP per country "
        "4. GDP per capita "
        "5. GDP annual growth rate "
        "6. Household Income "
        "Busca screenshots que contengan datos económicos de Google Market Finder. "
        "Organiza la información en formato tabular por país."
    ),
    expected_output=(
        "Tabla estructurada con los seis datos específicos del Economic Profile para cada país identificado. "
        "La tabla debe incluir columnas para país, tamaño de población, edad media, PIB del país, "
        "PIB per cápita, tasa de crecimiento anual y ingreso por hogar."
    ),
    tools=[image_tool],
    agent=data_collector
)

extract_trade_profile_task = Task(
    description=(
        "Revisa todos los screenshots en la carpeta {ecommerce_folder} y extrae específicamente la siguiente información del Trade Profile: "
        "1. Product Import Volume para cada país "
        "2. Export Potential para cada país "
        "3. Actual Exports para cada país "
        "4. Unrealized Export Potential para cada país "
        "5. Applied Tariffs para cada país "
        "Busca screenshots que contengan datos de ITC Trade Map. "
        "Organiza la información en formato tabular por país."
    ),
    expected_output=(
        "Tabla estructurada con los cinco datos específicos del Trade Profile para cada país identificado. "
        "La tabla debe incluir columnas para país, volumen de importación de productos, potencial de exportación, "
        "exportaciones actuales, potencial de exportación no realizado y aranceles aplicados."
    ),
    tools=[image_tool],
    agent=data_collector
)

#2. Análisis de Mercado
analyze_online_potential_task = Task(
    description=(
        "Analiza los datos del Online Profile para evaluar el potencial de mercado online "
        "de cada país. Considera el volumen de búsquedas, población activa en internet "
        "y costo de adquisición de clientes. Crea un ranking preliminar basado en "
        "oportunidades online."
    ),
    expected_output=(
        "Análisis detallado del potencial online de cada país con rankings justificados "
        "y recomendaciones preliminares basadas en datos de comportamiento online."
    ),
    agent=market_analyst
)

analyze_economic_viability_task = Task(
    description=(
        "Analiza los datos del Economic Profile para evaluar la viabilidad económica "
        "de cada mercado. Considera tamaño y crecimiento económico, poder adquisitivo "
        "y demografía. Crea un ranking preliminar basado en factores económicos."
    ),
    expected_output=(
        "Análisis detallado de la viabilidad económica de cada país con rankings justificados "
        "y recomendaciones preliminares basadas en factores económicos."
    ),
    agent=market_analyst
)

analyze_trade_opportunity_task = Task(
    description=(
        "Analiza los datos del Trade Profile para evaluar oportunidades comerciales específicas. "
        "Considera volumen de importaciones, potencial de exportación no realizado, "
        "barreras arancelarias y competencia existente. Crea un ranking preliminar "
        "basado en oportunidades comerciales."
    ),
    expected_output=(
        "Análisis detallado de oportunidades comerciales en cada país con rankings justificados "
        "y recomendaciones preliminares basadas en factores comerciales."
    ),
    agent=market_analyst
)

#3. Estrategia de Exportación
determine_top_countries_task = Task(
    description=(
        "Basándote en los análisis de perfil online, económico y comercial, determina los tres "
        "países con mayor potencial de exportación para el e-commerce analizado. "
        "Considera el balance entre volumen de mercado, facilidad de entrada, costos "
        "regulatorios y potencial de crecimiento."
    ),
    expected_output=(
        "Lista justificada de los tres países prioritarios para exportación, con clara "
        "explicación de los criterios utilizados y ventajas competitivas en cada mercado."
    ),
    agent=export_strategist
)

create_export_rationale_task = Task(
    description=(
        "Desarrolla un párrafo conciso que resuma los principales highlights por los cuales "
        "se eligieron los tres países prioritarios. Destaca factores diferenciadores y "
        "oportunidades específicas para la categoría de productos del e-commerce."
    ),
    expected_output=(
        "Párrafo de síntesis (máximo 150 palabras) que explique convincentemente por qué "
        "los tres países seleccionados representan las mejores oportunidades de exportación."
    ),
    agent=export_strategist
)

create_country_table_data_task = Task(
    description=(
        "Prepara los datos para la tabla comparativa de países que incluirá: País, Volumen de Búsqueda, "
        "Importaciones de Snowboards, Export Potential, Aranceles y Conclusión para cada país analizado. "
        "Utiliza la información recopilada para completar todos los campos requeridos."
    ),
    expected_output=(
        "Datos estructurados para la tabla comparativa de países, con todos los campos "
        "completados para cada país analizado."
    ),
    agent=export_strategist
)

#4. Generación de Reporte
create_country_table_data_task = Task(
    description=(
        "Prepara los datos para la tabla comparativa de países siguiendo EXACTAMENTE el formato mostrado en el ejemplo: "
        "Las columnas deben ser: "
        "1. País - nombre del país "
        "2. Volumen de Búsqueda (Google MF) - indicado con íconos de fuego para Alto/Medio/Muy alto o círculo amarillo para Bajo "
        "3. Importaciones de [Categoría de Producto] (ITC) - valor en formato $XXM con ícono de bolsa de dinero "
        "4. Export Potential - valor en formato $XXM con ícono de gráfica "
        "5. Aranceles - valor en porcentaje (0% con check verde o porcentaje con ícono rojo) "
        "6. Conclusión - texto breve que resuma la oportunidad (ej. 'Gran oportunidad DTC y B2B') "
        "Utiliza la información recopilada para completar todos los campos requeridos manteniendo el estilo visual consistente con el ejemplo."
    ),
    expected_output=(
        "Datos estructurados para la tabla comparativa de países, con todos los campos completados para cada país analizado, "
        "respetando exactamente el formato y estilo visual del ejemplo proporcionado."
    ),
    tools=[data_viz_tool],
    agent=export_strategist
)

compile_final_report_task = Task(
    description=(
        "Compila toda la información generada en un reporte final estructurado según el formato solicitado y guárdalo como archivo Markdown: "
        "1. Conclusión final con los tres países prioritarios en formato: 'Los tres países con mayor potencial de exportación son: País A, País B, País C.' "
        "2. Resumen de los highlights en un párrafo conciso (máximo 150 palabras) "
        "3. Tabla comparativa EXACTAMENTE con el formato del ejemplo proporcionado, incluyendo: "
        "   - País "
        "   - Volumen de Búsqueda (Google MF) con íconos de intensidad "
        "   - Importaciones de [Categoría de Producto] (ITC) con valores monetarios "
        "   - Export Potential con valores monetarios "
        "   - Aranceles con porcentajes e íconos "
        "   - Conclusión breve por país "
        "4. Sección de 'Datos Duros' organizada en tres categorías: "
        "   - Online Profile (datos de Google Market Finder) "
        "   - Economic Profile (datos económicos) "
        "   - Trade Profile (datos de ITC Trade Map) "
        "El formato debe ser profesional, claro y visualmente consistente con el ejemplo proporcionado. "
        "IMPORTANTE: Guarda el reporte como un archivo Markdown con el nombre 'Reporte_{ecommerce_url}.md', "
        "donde {ecommerce_url} es la URL del e-commerce analizado (utiliza solo el dominio principal, sin http/https o www)."
    ),
    expected_output=(
        "Reporte final completo y bien estructurado con todas las secciones requeridas, "
        "presentando la información de manera clara, profesional y accionable, "
        "manteniendo la consistencia visual con el ejemplo proporcionado. "
        "El reporte ha sido guardado como archivo Markdown con el nombre 'Reporte_{ecommerce_url}.md'."
    ),
    tools=[data_viz_tool, file_tool],
    agent=report_generator
)

# Asignar herramientas a los agentes
data_collector.tools = [image_tool, folder_tool]
market_analyst.tools = [market_tool]
export_strategist.tools = [market_tool, data_viz_tool]
report_generator.tools = [data_viz_tool]

#CREATING THE CREW
export_analysis_crew = Crew(
    agents=[data_collector, market_analyst, export_strategist, report_generator],
    tasks=[
        # Fase 1: Extracción de datos
        extract_online_profile_task, 
        extract_economic_profile_task, 
        extract_trade_profile_task,
        
        # Fase 2: Análisis de datos
        analyze_online_potential_task, 
        analyze_economic_viability_task, 
        analyze_trade_opportunity_task,
        
        # Fase 3: Estrategia de exportación
        determine_top_countries_task, 
        create_export_rationale_task,
        
        # Fase 4: Generación de reporte
        create_country_table_data_task,
        compile_final_report_task
    ],
    verbose=True
)

# Iniciar el proceso
result = export_analysis_crew.kickoff(
    inputs={
        "ecommerce_url": "URL_DEL_ECOMMERCE",
        "ecommerce_domain": process_url_for_filename("URL_DEL_ECOMMERCE"),  # Procesar la URL para el nombre del archivo
        "product_category": "CATEGORIA_DE_PRODUCTO",
        "ecommerce_folder": "PATH_TO_SCREENSHOTS_FOLDER"  # Carpeta donde están los screenshots
    }
)