# 🎵 La evolución del sonido — Dashboard interactivo

Dashboard interactivo construido con **Streamlit** y **Plotly Express** a partir del análisis exploratorio del Certamen 2 (Taller de Visualización de la Información, Universidad del Desarrollo).

**Pregunta que responde:** ¿cómo cambió el sonido de la música en Spotify entre 1921 y 2020 y qué perfiles de canciones se forman según sus características sonoras?

**App en vivo:** _(pegar aquí el enlace .streamlit.app)_

![Captura de la app](captura.png)

## Integrantes

- Catalina Ortega
- Joaquín Reyes

## Datos

- Fuente: Kaggle, *Spotify Dataset 1921-2020, 600k+ Tracks* (`tracks.csv`, 586.672 filas originales).
- Se aplicó la limpieza del Certamen 2 (nulos, `tempo = 0`, `time_signature = 0`, fechas fuera de rango, duplicados y canciones de más de 20 minutos).
- **Se trabaja con una muestra aleatoria de 40.000 canciones** (`random_state=42`), porque el archivo original pesa más de 25 MB. Está en `data/canciones_limpias.csv`.

## Qué incluye (versión beta 2.1.0)

- Filtros globales en el panel lateral: año, perfil de canción y contenido explícito.
- 4 KPIs con comparación contra el total sin filtros.
- Gráficos interactivos con Plotly Express: histograma, serie temporal, dispersión por perfil y radar.
- Segmentación K-Means (k = 5) con tabla de perfiles.

## Estructura del repositorio

```
├── app.py                     # La app de Streamlit
├── requirements.txt           # Librerías que instala Streamlit Cloud
├── data/
│   └── canciones_limpias.csv  # Muestra limpia del Certamen 2
├── .streamlit/
│   └── config.toml            # Tema visual
├── .gitignore
└── README.md
```

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```
