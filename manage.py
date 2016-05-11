#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'zhihu_spider'))


def get_praser():
    parser = argparse.ArgumentParser(description='Zhihu Spider')
    subparsers = parser.add_subparsers(help='sub-command help', dest='subcommand')
    # login
    _login = subparsers.add_parser('login', help='Login service')
    _login.add_argument('-d', '--demon', help='Run as demon.', action='store_true')
    _login.add_argument('-i', '--import-account', help='Import accounts from file(you should give the filename)')

    # shell
    subparsers.add_parser('shell', help='Shell service, for run and test')

    # db
    _db = subparsers.add_parser('db', help='db service, for create tables')
    _db.add_argument('--create-table', help='create-table', nargs='*')
    return parser

    # spider
    _spider = subparsers.add_parser('spider', help='Spider')
    _spider.add_argument('--demon', help='run as demon', action='store_true')


def main():
    parser = get_praser()
    args = parser.parse_args()
    if args.subcommand == 'shell':
        logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                            format='[%(asctime)s %(levelname)s] %(message)s')
        import IPython
        IPython.embed()
    elif args.subcommand == 'login':
        if args.demon:
            pass
        elif args.import_account:
            from login.manul_login import import_account_from_file
            import_account_from_file(filename=args.import_account)
        else:
            from login.manul_login import start_login
            start_login()
    elif args.subcommand == 'db':
        if 'create_table' in args:
            from db.db_engine import DBEngine
            db_engine = DBEngine()
            db_engine.create_db()

    elif args.subcommand == 'spider':
        pass

if __name__ == '__main__':
    main()
