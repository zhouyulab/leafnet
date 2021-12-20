from setuptools import setup, find_packages

setup(
    name='leafnet',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.model", "*.res", "*.dll", "*.so", "*.js"],
    },
    description='LeafNet is a convenient tool that can robustly localize stomata and segment pavement cells for light-microscope images.',
    author='Shaopeng Li',
    url='https://gitee.com/zhouyulab/leafnet',
    author_email='lishaopeng@whu.edu.cn',
    entry_points = {
        'console_scripts': [
          'leafnet-cli = leafnet.leafnet_cli:main',
          'leafnet-gui = leafnet.leafnet_gui:main',
          'leafnet-parser = leafnet.leafnet_parser:main'],
        # 'gui_scripts': [
        #   'leafnet-gui = leafnet.leafnet_gui:main']
     }
)