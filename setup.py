from setuptools import setup, find_packages

setup(
    name='quant-pyqt-ui',
    version='1.0.0',
    description='量化的pyqt界面',
    author='sykent',
    author_email='sykent.lao@gmail.com',
    packages=find_packages(),
    install_requires=[
        'PyQt5==5.15.4',
        'akshare==1.9.73',
        'numpy==1.23.2',
        'pandas==1.4.3',
        'QDarkStyle==3.1',
    ],
    entry_points={
        'console_scripts': [
            'myproject = quant-pyqt-ui.main:main'
        ]
    }
)
