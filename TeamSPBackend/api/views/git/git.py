# import git
import os
import sys
import re
import shutil
import stat
import errno
from django.http import HttpResponseNotAllowed, HttpResponse
from TeamSPBackend.common.utils import init_http_response, make_json_response
from TeamSPBackend.common.choices import RespCode

GIT_LOG = r'git -C {} log --pretty=tformat:%ae --shortstat --no-merges --> {}'
# GIT_LOG_TOTAL = r'git -C {} log --pretty=tformat:%an%n%ae%n%s --shortstat --no-merges --> {}'
GIT_LOG_TOTAL = r'git -C {} log --pretty=tformat:%H%n%an%n%ad%n%s --shortstat --no-merges --> {}'
GIT_LOG_INDIVIDUAL = r'git -C {} log --author={} --pretty=tformat:%H%n%an%n%ad%n%s --shortstat --no-merges --> {}'
# GIT_LOG_INDIVIDUAL = r'git -C {} log --author={} --pretty=tformat:%an%n%ae%n%s --shortstat --no-merges --> {}'
GIT_CLONE = r'git clone {} {}'

REPATTERN_FULL = r"\s(\d+)\D+(\d+)\D+(\d+)\D+\n"
REPATTERN_INSERT_ONLY = r"\s(\d+)\D+(\d+)\sinsertion\D+\n"
REPATTERN_DELETE_ONLY = r"\s(\d+)\D+(\d+)\sdeletion\D+\n"
PATH = './TeamSPBackend/api/views/git/repo'

def exec_git(url,path):
    git_clone_command = GIT_CLONE.format(url,path)
    os.system(git_clone_command)
    repo = path
    # logfile = './TeamSPBackend/api/views/git/gitstats.txt'
    # git_log_command = GIT_LOG.format(repo,logfile)
    # os.system(git_log_command)

    # commitfile = './TeamSPBackend/api/views/git/gitcommits.txt'
    # git_log_total_command = GIT_LOG_TOTAL.format(repo, commitfile)
    # os.system(git_log_total_command)
    #
    # lines = None
    # with open(commitfile, 'r', encoding='utf-8') as logfilehandler:
    #     lines = logfilehandler.readlines()
    # return lines
    return repo

def totalcommits(repo):
    commitfile = './TeamSPBackend/api/views/git/gitcommits.txt'
    git_log_command = GIT_LOG_TOTAL.format(repo, commitfile)
    os.system(git_log_command)
    lines = None
    with open(commitfile, 'r', encoding='utf-8') as logfilehandler:
        lines = logfilehandler.readlines()
    total_data = []
    total_commits = 0
    for i in range(0, len(lines), 6):
        commit_data = {}
        total_commits +=1
        commit_id = lines[i].strip()
        author = lines[i+1].strip()
        date = lines[i+2].strip()
        summary = lines[i+3].strip()
        file_changed = lines[i+5].strip()
        commit_data = {
            'commit_id': commit_id,
            'author': author,
            'date': date,
            'commit summary': summary,
            'file_changed': file_changed
        }
        total_data.append(commit_data)
    # print(total_data)
    os.remove(commitfile)
    data ={
        'total_commits': total_commits,
        'commit_data': total_data
    }
    return data

def individualcommit(repo,author):
    commitfile = './TeamSPBackend/api/views/git/gitcommits.txt'
    git_log_command = GIT_LOG_INDIVIDUAL.format(repo,author,commitfile)
    os.system(git_log_command)
    lines = None
    with open(commitfile, 'r', encoding='utf-8') as logfilehandler:
        lines = logfilehandler.readlines()
    individual_data = []
    for i in range(0, len(lines), 6):
        data = {}
        commit_id = lines[i].strip()
        author = lines[i + 1].strip()
        date = lines[i + 2].strip()
        summary = lines[i + 3].strip()
        file_changed = lines[i + 5].strip()
        data = {
            'commit_id': commit_id,
            'author': author,
            'date': date,
            'commit summary': summary,
            'file_changed': file_changed
        }
        individual_data.append(data)
    stat_data = parse(lines)
    data ={
        'stat_data': stat_data,
        'commit_data': individual_data
    }
    os.remove(commitfile)
    return data


def parse(lines):
    # commitfile = './TeamSPBackend/api/views/git/gitcommits.txt'
    #
    # with open(commitfile, 'r', encoding='utf-8') as logfilehandler:
    #     lines = logfilehandler.readlines()
    '''Analyse git log and sort to csv file.'''
    prog_full = re.compile(REPATTERN_FULL)
    prog_insert_only = re.compile(REPATTERN_INSERT_ONLY)
    prog_delete_only = re.compile(REPATTERN_DELETE_ONLY)

    stats = {}
    for i in range(0, len(lines), 6):
        author = lines[i+1].strip()
        #empty = lines[i+1]
        info = lines[i+5]
        #change = 0
        insert, delete = int(0), int(0)
        result = prog_full.search(info)
        if result:
            #change = result[0]
            insert = int(result.group(2))
            delete = int(result.group(3))
        else:
            result = prog_insert_only.search(info)
            if result:
                #change = result[0]
                insert = int(result.group(2))
                delete = int(0)
            else:
                result = prog_delete_only.search(info)
                if result:
                    #change = result[0]
                    insert = int(0)
                    delete = int(result.group(2))
                else:
                    print('Regular expression fail!')
                    return
        loc = insert - delete
        stat = stats.get(author)
        if stat is None:
            stats[author] = [1, insert, delete, loc]
        else:
            stat[0] += 1
            stat[1] += insert
            stat[2] += delete
            stat[3] += loc
    data ={
        'total_commits': stat[0],
        'insert': stat[1],
        'delete': stat[2],
        'modified': stat[3]
    }
    return data


def set_rw(operation, name, exc):
     os.chmod(name, stat.S_IWRITE)
     os.remove(name)

def getCommitTotal(request):

    URL = request.POST.get('git_url')
    REPO = exec_git(URL, PATH)
    log_commit = totalcommits(REPO)
    shutil.rmtree(PATH, ignore_errors=False, onerror=set_rw)
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = log_commit
    return make_json_response(HttpResponse, resp)


def getCommmitperTeamMember(request):
    URL = request.POST.get('git_url')
    REPO = exec_git(URL, PATH)
    AUTHOR = "'" + request.POST.get('author')+"'"
    log_commit = individualcommit(REPO,AUTHOR)
    shutil.rmtree(PATH, ignore_errors=False, onerror=set_rw)
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = log_commit

    return make_json_response(HttpResponse, resp)

    # URL = request.POST.get('git_url')
#     LINES = exec_git(URL, PATH)
#     log_commit = commits(LINES)
#     shutil.rmtree(PATH, ignore_errors=False, onerror=set_rw)


    # print('gitstats begin')
    #
    # URL = request.POST.get('git_url')
    # # URL = 'https://github.com/LikwunCheung/TeamSPBackend.git'
    # # REPO = git.Repo.clone_from(url=URL, to_path=PATH)
    # # REPO = "C:/Users/Procyon/Desktop/TeamSPBackend"
    # LINES = exec_git(URL,PATH)
    # # STATS = parse(LINES)
    # log_commit = totalcommits(LINES)
    # resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    # resp['data'] = log_commit
    # return make_json_response(HttpResponse, resp)
    # # print(log_commit)
    #
    # shutil.rmtree(PATH, ignore_errors=False, onerror=set_rw)


# if __name__ == "__main__":
#     getCommmitperTeamMember()
