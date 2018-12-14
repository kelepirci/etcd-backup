#!/usr/bin/env .venv/bin/python

import boto3
import click
import logging
import subprocess
import shutil
import uuid
import time
import os
from logging.config import dictConfig


@click.command()
@click.option('--debug_enabled', is_flag=True, help="Enables DEBUG logging.")
@click.option('--aws_access_key', required=True, help="AWS Account access key ID.")
@click.option('--aws_secret_key', required=True, help="AWS Secret key of the access key.")
@click.option('--aws_s3_bucket', required=True, help="AWS Secret key of the access key.")
@click.option('--aws_s3_region', help="AWS Region for S3 bucket.")
@click.option('--etcd_v2_datadir', type=str, help="v2 key type data directory.")
@click.option('--etcd_v3_endpoints', type=str, help="v3 etcd endpoint.")
@click.option('--prefix', type=str, help="Prefix for backup file on S3.")
def all_procedure(debug_enabled,
                  aws_access_key,
                  aws_secret_key,
                  aws_s3_bucket,
                  aws_s3_region,
                  etcd_v2_datadir,
                  etcd_v3_endpoints,
                  prefix):
    # logging configuration goes here
    log_level = logging.INFO

    if debug_enabled:
        log_level = logging.DEBUG

    logging_config = dict(
        version=1,
        formatters={
            'f': {'format':
                      '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
        },
        handlers={
            'h': {'class': 'logging.StreamHandler',
                  'formatter': 'f',
                  'level': log_level}
        },
        root={
            'handlers': ['h'],
            'level': log_level,
        },
    )

    dictConfig(logging_config)
    logger = logging.getLogger()
    logger.debug('Debug enabled')

    tmp_dir = str(uuid.uuid4())
    env_vars = {'ETCDCTL_API': '2'}

    # v2 key backup
    def v2_backup():
        logger.info('Starting to backup up etcd v2 key data...')
        logger.info('Running "etcdctl backup" command...')
        p = subprocess.Popen([
            "etcdctl backup --data-dir %s --backup-dir /tmp/%s" % (etcd_v2_datadir, tmp_dir),
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env_vars)
        logger.info(p.communicate())

    # tar gzip backup files
    def compress_backup_files():
        logger.info('Compressing backup files...')
        shutil.make_archive("/tmp/%s" % tmp_dir, 'zip', "/tmp/%s/" % tmp_dir)

    # upload compressed file to s3 bucket
    def upload_s3():
        date_time = time.strftime("%Y-%m-%d-%H%M%S")
        s3 = boto3.resource('s3')
        logger.info('Uploading backup to s3 bucket')
        s3.Object(aws_s3_bucket, 'k8s_%s_%s.zip' % (prefix,date_time)).put(Body=open('/tmp/%s.zip' % tmp_dir, 'rb'))

    # cleanup temp directory
    def clean_temp():
        logger.info('Cleaning /tmp/%s ...' % tmp_dir)
        try:
            shutil.rmtree("/tmp/%s/" % tmp_dir)
        except OSError as e:
            logger.error("Error: %s - %s." % (e.filename, e.strerror))
        os.remove("/tmp/%s.zip" % tmp_dir)
        logger.info('/tmp/%s file deleted' % tmp_dir)

    # check if v2_datadir or v3_endpoint set
    # if not set exit with error log
    if not etcd_v2_datadir and not etcd_v3_endpoints:
        logger.error('--etcd_v2_datadir or --etcd_v3_endpoints must be set.')
        exit()

    # v2 key backup
    if etcd_v2_datadir:
        logger.info('etcd v2 backup enabled!')
        v2_backup()
        compress_backup_files()
        upload_s3()
        clean_temp()


if __name__ == "__main__":
    all_procedure()


def v3_backup():
    pass


def upload_to_s3():
    pass
