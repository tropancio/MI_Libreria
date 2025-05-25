from setuptools import setup, find_packages

setup(
    name="mi_libreria_cruzes",
    version="0.1",
    packages=['Mi_Libreria', 'Mi_Libreria.Cruze', 'Mi_Libreria.DB', 'Mi_Libreria.Funcionalidad', 'Mi_Libreria.Principal', 'Mi_Libreria.SII'],    install_requires=[
        "pandas", 
        "numpy",
        "IPython",
        "ipywidgets",
        "ipydatagrid",
        "playwright>=1.40.0",
        "python-dotenv>=1.0.0",
        "selenium>=4.0.0",
        "pyodbc>=4.0.0"
    ],
    extras_require={
        "sii-playwright": [
            "playwright>=1.40.0",
            "python-dotenv>=1.0.0"
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=5.0.0"
        ]
    },
    author="Tu Nombre",
    description="Librería para cruces de datos, procesamiento avanzado y automatización SII con Playwright",
    url="https://github.com/tu_usuario/mi_libreria_cruzes",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
