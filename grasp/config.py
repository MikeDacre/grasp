"""
Manage a persistent configuration for the database.

       CREATED: 2016-10-10
 Last modified: 2016-10-10 14:32

"""
import os
import configparser

CONFIG_FILE = os.path.expanduser("~/.grasp")

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

def init_config(db_type, db_file='', db_host='', db_user='', db_pass=''):
    """Create an initial config file."""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    config['DEFAULT'] = {'DatabaseType': db_type}
    config['sqlite']  = {'DatabaseFile': db_file}
    config['other']   = {'DatabaseHost': db_host,
                         'DatabaseUser': db_user,
                         'DatabasePass': db_pass}
    with open(CONFIG_FILE, 'w') as fout:
        config.write(fout)
    # Make config only accessible to user
    os.chmod(CONFIG_FILE, 0o600)
