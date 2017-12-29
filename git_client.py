from git_vars import *


def git_client_clone():
    return git_client_exec('git clone %s . -q' % git_server_repo_url)


def git_client_exec(command):
    return os.system('GIT_SSH_COMMAND="ssh -i %s" GIT_MERGE_AUTOEDIT=no %s' % (private_key_file_path, command) )
