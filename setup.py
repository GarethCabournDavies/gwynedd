import setuptools
import os

def list_all_scripts(base_path):
    script_list = []
    for file_or_dir in os.listdir(base_path):
        full_path = os.path.join(base_path, file_or_dir)
        if os.path.isdir(full_path):
            script_list += list_all_scripts(full_path)
        else:
            script_list += [full_path]
    return script_list

setuptools.setup(
name = 'gwynedd',
version = '0.0.0',
packages = setuptools.find_packages(),
scripts = list_all_scripts('bin')
)
