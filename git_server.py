import docker
import git
import shutil
from git_vars import *


def git_server_build(cpus):
    """
    Builds and starts git server docker container with one repo.

    :param cpus: Relative maximum CPU assignment ranging from 0.0 to 1.0.
    :return: GitServerDocker wrapper
    """

    if os.path.exists('%s' % git_server_rel_path):
        shutil.rmtree('%s' % git_server_rel_path)

    _git_server_repo_build()
    _git_server_keys_store_build()

    return _git_server_container_build(cpus)


class GitServerDocker:
    def __init__(self, container):
        self._container = container

    def dispose(self):
        if self._container is not None:
            self._container.stop()
            self._container.remove()
            self._container = None


def _git_server_repo_build():
    repo_path = '%s/%s' % (git_server_rel_path, git_server_repo_name)
    file_path = '%s/%s' % (repo_path, git_server_repo_file_name)
    os.makedirs(repo_path)

    repo = git.Repo.init(repo_path, shared=True)

    with open(file_path, 'a') as f:
        f.write('Hello world!')
        f.close()

    repo.index.add([file_path])
    repo.index.commit('Initial commit.')

    repo.clone('%s/%s.git' % (git_server_repos_rel_path, git_server_repo_name), bare=True)
    shutil.rmtree(repo_path)


def _git_server_keys_store_build():
    os.makedirs(git_server_keys_rel_path)
    shutil.copy(public_key_file_path, git_server_keys_rel_path)


def _git_server_container_build(cpus):
    cpu_period = 100000
    cpu_quota = int(cpu_period * cpus)

    volumes = {
        git_server_keys_rel_path: {'bind': '/git-server/keys', 'mode': 'rw'},
        git_server_repos_rel_path: {'bind': '/git-server/repos', 'mode': 'rw'}
    }

    ports = {
        '22/tcp': 2222
    }

    container = docker.from_env().containers.run(image='jkarlos/git-server-docker',
                                                 cpu_period=cpu_period,
                                                 cpu_quota=cpu_quota,
                                                 volumes=volumes,
                                                 ports=ports,
                                                 detach=True)

    return GitServerDocker(container)
