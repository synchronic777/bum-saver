import os
from os import environ
from tools.utils import log, get_dt, req_installed, get_settings
from os.path import join, exists
import platform
import shutil
import venv


def setup_print(step, lvl, message, *args):
    """Standardizes the output format
    :param step, short string that indicates to the user the step we are going through
    :param lvl, letter that indicates if the displayed message is an Info, Warning or Error
    :param message, the message we want to print
    """
    uid = None
    log_type = 'exec'
    if step == 'setup':
        log_type = step
    if step == 'uninstall':
        log_type = step
    if len(args) > 0:
        uid = args[0]
    string = f"[{(f'{uid}:' if uid else '')}{get_dt()}:{step}][{lvl}] {message}"
    log(string, log_type)
    print(string)


def setup():
    project_data = os.listdir()
    filtered_data = []
    for elem in project_data:
        append = True
        if elem == 'venv':
            append = False
        if elem == '__pycache__':
            append = False
        if elem == '.idea':
            append = False
        if append:
            filtered_data.append(elem)
    settings = get_settings()
    home = os.path.expanduser("~")
    abs_setup_path = f'{home}/{settings["rel_setup_path"]}'
    setup_folder = f'{abs_setup_path}/shlerp/'
    current_os = platform.uname().system

    # Determine on which OS the script is running
    if current_os in ('Darwin', 'Linux'):
        count = 0
        for elem in filtered_data:
            if exists(f'{setup_folder}{elem}'):
                count += 1

        # Step 1: Copy the files into the setup folder
        # Check if the project files are all installed. If so, notify the user
        if count == len(filtered_data):
            setup_print('setup', 'I', '[1/3] OK: Project files already installed')
        else:
            try:
                if not exists(setup_folder):
                    os.makedirs(setup_folder)
                for elem in filtered_data:
                    try:
                        shutil.copy(f'./{elem}', f'{setup_folder}{elem}')
                    except IsADirectoryError:
                        shutil.copytree(f'./{elem}', f'{setup_folder}{elem}')
                    os.chmod(f'{setup_folder}{elem}', 0o500)
                    setup_print('setup', 'I', f'[1/3] OK: {setup_folder}{elem}')
                setup_print('setup', 'I', f'[1/3] OK: Copied the project into {setup_folder}')
            except FileNotFoundError as not_found_err:
                setup_print('setup', 'E', f'[1/3]{not_found_err}')

        # Step 2: Add the alias into .bashrc/.zshrc
        shell = environ['SHELL']
        shell_string = shell.split('/')[2] if 'bash' in shell or 'zsh' in shell else None
        if not shell_string:
            setup_print('setup', 'E', '[2/3] Please use a bash or zsh shell to install the command system-wide')
        else:
            rc_file = f'.{shell_string}rc'
            read_rc = None
            if exists(f'{home}/{rc_file}'):
                with open(f'{home}/{rc_file}', 'r') as read_rc:
                    read_rc = read_rc.read()

            with open(f'{home}/{rc_file}', 'a') as write_rc:
                write = True
                if read_rc:
                    if 'shlerp' in read_rc:
                        write = False
                        setup_print('setup', 'I', '[2/3] OK: Alias function already installed')
                if write:
                    write_rc.write(f'source {setup_folder}config/function.template')
                    setup_print('setup', 'I', f'[2/3] OK: Alias added to {rc_file}')

        def check_deps(first_try):
            word = 'successfully'
            if not first_try:
                word = 'already'
            if req_installed(setup_folder):
                setup_print('setup', 'I', f'[3/3] OK: Virtual environment {word} installed')
                setup_print('setup', 'I', f'✅ Install complete! Please restart your terminal to use the shlerp command')
            else:
                setup_print('setup', 'E', 'ERROR: A problem happened during the requirements installation')
                exit(0)
        # Step 3: Create a venv in the setup folder and install the requirements
        venv_folder = join(setup_folder, "venv")
        if not exists(venv_folder):
            venv.create(venv_folder, with_pip=True)
            # Then proceed with the requirements installation
            check_deps(True)
        else:
            check_deps(False)

    else:
        setup_print('setup', 'E', 'ERROR: Shell or system not supported')
        exit(0)


if __name__ == '__main__':
    setup()
