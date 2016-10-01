#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
import os
import json

from ftplib import FTP
from ftplib import error_proto, error_perm, all_errors
from subprocess import check_call, CalledProcessError
from datetime import datetime, timedelta

class FtpAction(object):
    def __init__(self, host, user, pwd):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.flag = "_SUCCESS"
        self.ftp = None
        self.remote_dir_already_checked = []

    def traverse_remote(self):
        """
        traverse remote ftp dir /GreyList
        """
        filelist = []

        try:
            self.ftp = FTP(self.host, user=self.user, passwd=self.pwd, timeout=300)
            self.ftp.set_pasv(True)
            logger.debug('traverse remote ftp server...')
            filelist = self.get_remote_dir(get_conf_string('ftp', 'gl'))
        except Exception as e:
            logger.exception(e)
            logger.error('traverse remote file list failed')
        return filelist

    def traverse_local(self):
        logger.debug('traverse local files which had been downloaded...')
        filelist = self.get_local_dir(get_conf_string('hdfs', 'filelist'))
        return filelist

    def get_local_dir(self, filename):
        """
        read filelist.json which in hdfs's /
        """
        try:
            if not self.hdfs_client.get_client().status(filename,
                                                        strict=False):
                self.hdfs_client.get_client().write(filename, data='')
        except:
            raise HdfsError
        with self.hdfs_client.get_client().read(filename) as f:
            data = f.read()

        return get_data_from_json(data)

    def get_remote_dir(self, path):
        """
        返回 sftp 中的文件列表
        每一项为文件的绝对路径
        """
        temp = [p for p in self.ftp.nlst(path)]

        dirs = []

        # ignore the outdated folders
        for path in temp:

            if path in self.remote_dir_already_checked:
                # too much log
                # logger.debug('remote path %s already processed before, no further action needed', path)
                continue

            # path is like '/GreyList/2016010101', so urllog is like '2016010101'
            urllog = path.split('/')[2]

            if urllog_is_outofdate(urllog) == True:
                logger.debug('ignore the folders %s uploaded long time ago', path)
                self.remote_dir_already_checked.append(path)

            else:
                dirs.append(path)

        return [os.path.join(d, os.path.basename(d))
                for d in dirs if self.remote_file_is_legal(d)]

    def update_file_list(self, files, add=True):
        """
        将更新后的文件列表写入 filelist.json
        读取已经现有的filelist文件
        append 新的 list
        """
        if not files:
            return
        filelist = get_conf_string('hdfs', 'filelist')
        try:
            old_data = self.hdfs_client.read_hdfs_file(filelist)
        except:
            raise HdfsError
        old_files = get_data_from_json(old_data)
        if (add):
            if isinstance(files, list):
                old_files.extend(files)
            elif isinstance(files, basestring):
                old_files.append(files)
        else:
            old_files.remove(files)

        new_data = json.dumps(list(set(old_files)))
        self.hdfs_client.write_hdfs_file(filelist, data=new_data)

    def add_local_filelist_to_checked_set(self, filelist):

        logger.debug('add local file list to already checked set')
        self.remote_dir_already_checked = []

        for local_path in filelist:

            remote_path = os.path.join(get_conf_string('ftp', 'gl'), os.path.basename(local_path))
            self.remote_dir_already_checked.append(remote_path)

    def update(self):
        """
        获取 sftp 服务器中的文件列表
        获取 hdfs 中存储的文件列表

        比较 hdfs 中缺少的文件列表
        每一项为 hdfs 绝对路径
        """
        remote_dict = {}
        remote_name_list = []

        local_list = self.traverse_local()
        self.add_local_filelist_to_checked_set(local_list)

        remote_list = self.traverse_remote()

        for remote in remote_list:
            name = os.path.basename(remote)

            if urllog_is_outofdate(name) == True:
                logger.debug('original urllog %s is out of date, ignore', name)

            else:
                remote_dict[name] = remote
                remote_name_list.append(name)

        local_set = set(os.path.basename(i) for i in local_list)
        remote_set = set(remote_name_list)

        #self.update_file_list(remote_name_list)
        download_list = remote_set.difference(local_set)
        d = [remote_dict[name] for name in download_list]
        if d:
            logger.debug('these files need to be downloaded: %(filelist)s',
                         {'filelist': d})
        return d

    def start(self):
        files = self.update()
        urllog_dir = get_conf_string('local', 'urllog_dir')
        files = sorted(files,
                       cmp=lambda x,y: cmp(int(os.path.basename(x)), int(os.path.basename(y))),
                       reverse=True)
        for f in files[:5]:
            loc_filepath = convert_remote_filename_to_local(f, urllog_dir)
            self.sftp_to_local(f, loc_filepath)

            # self.delete_ftp_dir(os.path.dirname(f))
            yield loc_filepath

    def ftp_init(self, retry=2):
        try:
            self.ftp = FTP(self.host, user=self.user, passwd=self.pwd,timeout=300)
            self.ftp.set_pasv(True)
        except Exception as e:
            if retry > 0:
                retry -= 1
                self.ftp_init(retry)
            else:
                logger.error('ftp init failed, please check the network, waiting till next time...')

    def delete_ftp_file(self, filename):
        try:
            self.ftp_init()
            self.ftp.delete(filename)
        except Exception as e:
            logger.error('FTP exception occur during deleting ftp file')

    def delete_ftp_dir(self, dirname):
        try:
            self.delete_ftp_file(os.path.join(dirname, os.path.basename(
                dirname)))
            self.delete_ftp_file(os.path.join(dirname, self.flag))
            self.ftp.rmd(dirname)
            logger.debug('delete dir name %s' % dirname)
        except error_perm:
            logger.error('delete dir failed %(dirname)s, no permission', {'dirname': dirname})
        except Exception as e:
            logger.error('FTP delete ftp dir failed, wait for next time...')

    def remote_file_is_legal(self, filename):
        logger.debug('detect %(filename)s if file is ready to download',
                     {'filename': filename})
        try:
            list_dir = self.ftp.nlst(filename)
            return os.path.join(
                filename, self.flag) in list_dir and os.path.join(
                    filename, os.path.basename(filename)) in list_dir
        except all_errors:
            self.ftp_init()
            return False

    def local_file_is_legal(self, filename):
        pass

    def local_to_sftp(self, localpath, remotepath):

        try:
            self.ftp_init()
            fp = open(localpath, 'rb')
            success = open(get_conf_string('local', 'sucpath'), 'rb')
            logger.debug('upload %(localpath)s to %(remotepath)s...',
                         {'localpath': localpath,
                          'remotepath': remotepath})
            self.ftp.mkd(remotepath)
            self.ftp.storbinary('STOR ' + os.path.join(
                remotepath, os.path.basename(remotepath)), fp)
            self.ftp.storbinary('STOR ' + os.path.join(remotepath, self.flag),
                                success)
        except IOError:
            logger.error('FTP exception occur during uploading process, IOError')
        except OSError:
            logger.error('FTP exception occur during uploading process, OSError')
        except error_perm:
            """
            文件夹已存在，则新建时间戳+1的新文件夹
            """
            d = os.path.dirname(remotepath)
            f = str(int(os.path.basename(remotepath)) + 1)
            self.local_to_sftp(localpath, os.path.join(d, f))
        fp.close()
        return remotepath

    def sftp_to_local(self, remotepath, localpath):
        """
        从 sftp 下载文件到 linux 本地文件系统
        """
        try:
            self.ftp_init()
            dirname = os.path.dirname(localpath)
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            try:
                os.chdir(dirname)
                check_call(['wget', '--timeout=30','--tries=3', '--no-clobber', '-c','--user=' + self.user, '--password=' +
                            self.pwd, 'ftp://%s' % self.host + remotepath])
            except CalledProcessError:
                pass
        except Exception as e:
            logger.exception(e)
            logger.error('FTP download file error...')
        return os.path.basename(remotepath)

    def folder_exists(self, ftp_path, folder_path):

        ret = False

        try:
            # already init at caller
            # self.ftp_init()

            # list all folder_path in ftp_path
            all_folder_path = self.ftp.nlst(ftp_path)

            # check if folder in folder_path
            if folder_path in all_folder_path:
                ret = True

        except Exception as e:
            logger.exception(e)

        return ret

    def upload_folder(self, folder_path, folder, ftp_path):

        ret = 0
        remotepath = os.path.join(ftp_path, folder)

        logger.debug('uploading folder %s from %s to %s ...', folder, folder_path, remotepath)

        try:
            self.ftp_init()

            # if path not exists
            if self.folder_exists(ftp_path, remotepath) != True:

                # ftp create remote folder
                self.ftp.mkd(remotepath)
                logger.debug('create remote path: %s', remotepath)

            else:
                logger.debug('path already exists', remotepath)

            # for each file in folder
            for filename in os.listdir(folder_path):

                # calc file path
                file_path = os.path.join(folder_path, filename)

                # try upload the file
                try:
                    with open(file_path) as fp:

                        ftp_path = os.path.join(remotepath, filename)
                        self.ftp.storbinary('STOR ' + ftp_path, fp)
                        logger.debug('upload %s to path %s', filename, ftp_path)

                except Exception as e:
                    logger.exception(e)
                    ret = -1

                if ret == -1:
                    break
        except Exception as e:
            logger.exception(e)
            ret = -1

        return ret