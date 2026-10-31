import os

def listar_directorios_archivos(ruta_proyecto) -> None:
    """
    Método que imprime una lista de todos los archivos y directorios dentro del directorio raíz del proyecto,
    excluyendo la carpeta 'env', archivos ocultos y la carpeta '.git'.

    :return:
        - None
    """
    for root, dirnames, filenames in os.walk(ruta_proyecto):
        # Ignorar la carpeta 'env'
        if 'env' in dirnames:
            dirnames.remove('env')
        if '.venv' in dirnames:
            dirnames.remove('.venv')
        if '.vscode' in dirnames:
            dirnames.remove('.vscode')
        if '.git' in dirnames:
            dirnames.remove('.git')
        if '__pycache__' in dirnames:
            dirnames.remove('__pycache__')
        level = root.replace(ruta_proyecto, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        # Ignorar archivos ocultos
        for f in filenames:
            if not f.startswith('.'):
                print(f'{subindent}{f}')

ruta_proyecto = r"C:\Users\brink\Music\Z#\WORKSPACE\ComponentVersionCatalog"
listar_directorios_archivos(ruta_proyecto)