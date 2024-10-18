from setuptools import setup, find_packages

setup(
    name='stock-viewer',
    version='0.1',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        'PyQt5',
        'yfinance'
    ],
    entry_points={
        'console_scripts': [
            'stock-viewer-program=stock_viewer.prog_viewer:main',  # Apontando para a função principal em main.py
            'stock-editor-program=stock_viewer.prog_editor:main',  # Apontando para a função principal em main.py
        ],
    },
    author='Fernando Pujaico Rivera',
    author_email='fernando.pujaico.rivera@gmail.com',
    description='Um visualizador de ações',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/trucomanx/stock-viewer',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

