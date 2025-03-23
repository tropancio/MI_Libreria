from setuptools import setup, find_packages

setup(
    name="mi_libreria_cruzes",
    version="0.1",
    packages=find_packages(),
    install_requires=["pandas", "numpy","IPython","ipywidgets"],
    author="Tu Nombre",
    description="Librería para cruces de datos y procesamiento avanzado",
    url="https://github.com/tu_usuario/mi_libreria_cruzes",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
