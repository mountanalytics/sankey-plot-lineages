from setuptools import setup, find_packages

setup(
    name='sankeyapp',
    version='0.1',
    packages=find_packages(include=['sankeyapp', 'sankeyapp.*']),  # Only include the sankeyapp package
    include_package_data=True,  # Include non-code files specified in MANIFEST.in
    install_requires=[
        'flask',
        'plotly',
        'pandas'
    ],
    entry_points={
        'console_scripts': [
            'sankeyapp=sankeyapp.app:main',  # Command to start the app
        ],
    },
    package_data={
        '': ['templates/*.html'],  # Include template files in the package
    },
)