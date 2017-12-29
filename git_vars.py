import os


_repo_root = os.getcwd()
public_key_file_name = 'id_rsa.pub'
public_key_file_path = '%s/%s' % (_repo_root, public_key_file_name)
private_key_file_name = 'id_rsa'
private_key_file_path = '%s/%s' % (_repo_root, private_key_file_name)

git_rel_path = os.path.expanduser('~/ldtst-git')
git_client_rel_path = git_rel_path + '/client'
git_server_rel_path = git_rel_path + '/server'
git_server_keys_rel_path = git_server_rel_path + '/keys'
git_server_repos_rel_path = git_server_rel_path + '/repos'

git_server_repo_name = 'r_1'
git_server_repo_file_name = 'f_1.txt'
git_server_repo_url = 'ssh://git@localhost:2222/git-server/repos/%s.git' % git_server_repo_name
