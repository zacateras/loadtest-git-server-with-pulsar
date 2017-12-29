from git_vars import *


def git_client_clone():
    git_client_exec('git clone %s .' % git_server_repo_url)


def git_client_exec(command):
    os.system('GIT_SSH_COMMAND="ssh -i %s/%s" %s' % (git_vars_cwd, git_server_private_key_file_name, command))
