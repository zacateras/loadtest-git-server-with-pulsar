import os

from git import Repo


def init_repo(repo_dir):
    Repo.init(repo_dir)

class GitCreator:
    """
    Creates git object
    """

    def __init__(self, remote_repo_name, repo_dir, file_list, commit_message):
        self.remote_repo_name = remote_repo_name
        self.file_list = [file_list]
        self.commit_message = commit_message
        self.repo_dir = repo_dir
        self.repo = Repo(repo_dir)

    def create_new_repo_gihub(self):
        """Create specific git repo on Github"""

        login = "savchuknd"
        token = "a37e139725b4740d2e8e15bdd76168c319356612"
        os.system("curl -u \"" + login + ":" + token + "\" https://api.github.com/user/repos "
                                                       "-d '{\"name\":\"'%s'\"}'" % self.remote_repo_name)

    def repo_add(self):
        """Add file to git"""

        self.repo.index.add(self.file_list)

    def repo_commit(self):
        """Commit changes with commit message"""

        self.repo.index.commit(self.commit_message)

    def repo_push(self):
        """Push to git repo"""

        # change /Users/savchuk/PycharmProjects/load-test-git to your's project location
        os.chdir('/Users/savchuk/PycharmProjects/load-test-git/REPO_ROOT/git/client/{0}'.format(self.remote_repo_name))
        os.system('git remote add origin https://github.com/savchukndr/{0}'.format(self.remote_repo_name))
        os.system('git push origin master')


if __name__ == "__main__":
    i = GitCreator()
    i.create_new_repo_gihub()
