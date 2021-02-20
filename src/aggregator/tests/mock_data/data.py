import os

dir = os.path.dirname(__file__)


def common_rss():
    file_path = os.path.join(dir, 'common_rss.xml')
    with open(file_path, 'r') as f:
        return f.read().replace('\n', '')


def github():
    file_path = os.path.join(dir, 'github.xml')
    with open(file_path, 'r') as f:
        return f.read().replace('\n', '')


def remotejob():
    file_path = os.path.join(dir, 'remote-job.xml')
    with open(file_path, 'r') as f:
        return f.read().replace('\n', '')
