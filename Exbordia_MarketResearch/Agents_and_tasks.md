AGENTES

# Data Collector Agent
data_collector = Agent(
    role="Data Collector",
    goal="Extraer con precisión datos de screenshots relacionados con investigación de mercado",
    backstory="Eres un especialista en extracción de datos que puede interpretar información visual de Google Market Finder e ITC Trade Map. Tu habilidad para organizar datos estructurados es fundamental para el análisis posterior.",
    allow_delegation=True,
    verbose=True
)

# Market Analyst Agent
market_analyst = Agent(
    role="Market Analyst",
    goal="Analizar datos de mercado e identificar tendencias y oportunidades comerciales",
    backstory="Como analista de mercados internacionales, tienes experiencia evaluando datos económicos y de comportamiento online para determinar la viabilidad de nuevos mercados. Tu análisis será crucial para identificar los países con mayor potencial.",
    allow_delegation=True,
    verbose=True
)

# Export Strategist Agent
export_strategist = Agent(
    role="Export Strategist",
    goal="Determinar los mejores países para exportación basado en criterios múltiples",
    backstory="Eres un estratega de exportación con amplia experiencia en comercio internacional. Tu especialidad es evaluar factores como aranceles, potencial de exportación, volumen de búsquedas y datos económicos para recomendar los mercados óptimos.",
    allow_delegation=True,
    verbose=True
)

# Report Generator Agent
report_generator = Agent(
    role="Report Generator",
    goal="Crear un informe estructurado y cohesivo sobre potencial de exportación",
    backstory="Especialista en comunicación de datos complejos de manera clara y estructurada. Tu habilidad para sintetizar información y presentarla en formatos accesibles es fundamental para que los stakeholders puedan tomar decisiones informadas.",
    allow_delegation=False,
    verbose=True
)


TASKS
extract_online_profile_task = Task(
    description=(
        "Extrae y estructura todos los datos del Online Profile de los screenshots proporcionados. "
        "Identifica claramente valores de búsquedas mensuales, población activa en internet y "
        "costos recomendados de Google Ads para cada país mostrado. "
        "Organiza los datos en un formato estructurado que pueda ser utilizado para análisis posterior."
    ),
    expected_output=(
        "Tabla estructurada con datos de Online Profile para cada país, incluyendo búsquedas mensuales, "
        "población activa en internet y costos de Google Ads. Los datos deben estar correctamente "
        "etiquetados por país y métricas."
    ),
    agent=data_collector
)

extract_economic_profile_task = Task(
    description=(
        "Extrae y estructura todos los datos del Economic Profile de los screenshots proporcionados. "
        "Identifica valores de población, edad media, PIB por país, PIB per cápita, "
        "tasa de crecimiento anual y ingresos por hogar para cada país mostrado. "
        "Organiza los datos en un formato estructurado para análisis posterior."
    ),
    expected_output=(
        "Tabla estructurada con datos económicos para cada país, incluyendo población, PIB, "
        "PIB per cápita, tasa de crecimiento y datos de ingresos. Los datos deben estar correctamente "
        "etiquetados por país y métricas."
    ),
    agent=data_collector
)

extract_trade_profile_task = Task(
    description=(
        "Extrae y estructura todos los datos del Trade Profile de los screenshots de ITC Trade Map. "
        "Identifica volumen de importación, potencial de exportación, exportaciones actuales, "
        "potencial de exportación no realizado y aranceles aplicados para cada país mostrado. "
        "Organiza los datos en un formato estructurado para análisis posterior."
    ),
    expected_output=(
        "Tabla estructurada con datos comerciales para cada país, incluyendo importaciones, "
        "exportaciones potenciales y actuales, potencial no realizado y aranceles. "
        "Los datos deben estar correctamente etiquetados por país y métricas."
    ),
    agent=data_collector
)