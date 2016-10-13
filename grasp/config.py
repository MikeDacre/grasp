"""
Manage a persistent configuration for the database.

       CREATED: 2016-10-10
 Last modified: 2016-10-12 16:56

"""
import os
import configparser
import readline

CONFIG_FILE = os.path.expanduser("~/.grasp")

config = configparser.ConfigParser()
config.read(CONFIG_FILE)


###############################################################################
#                        Config Manipulation Functions                        #
###############################################################################


def init_config_interactive():
    """Interact with the user to create a new config."""
    # Use tab completion
    t = tabCompleter()
    readline.set_completer_delims('\t')
    readline.parse_and_bind("tab: complete")

    # Get permission
    t.createListCompleter(['y', 'n'])
    readline.set_completer(t.listCompleter)
    print("Do you want to initialize your config at {}"
            .format(CONFIG_FILE))
    print("This will erase your current configuration (if it exists)")
    choice = input("Initialize config? [y/N] ").strip().lower()
    if not choice == 'y':
        return

    # Get choices with tab completion
    t.createListCompleter(["sqlite", "mysql", "postgresql"])
    readline.set_completer(t.listCompleter)
    print("What kind of database do you want to use?")
    db_type = input('sqlite/postgres/mysql ').strip().lower()

    setup_other = False
    file_path, host, user, passwd, host_string = ('',)*5

    # Initialize for sqlite
    if db_type.lower() == 'sqlite':
        readline.set_completer(t.pathCompleter)
        print("Where would you like to put the db file?")
        file_path = os.path.expanduser(input('PATH: [~/grasp.db] ')).strip(' ').lower()
        if not file_path:
            file_path = os.path.expanduser('~/grasp.db')
        setup_other = True if input("Also setup postgres/mysql auth? [y/N] ") \
            == 'y' else False

    # Initialize for other
    elif db_type.lower() == 'postgresql' or db_type.lower() == 'mysql':
        setup_other = True

    else:
        print("Invalid db choice {}".format(db_type))
        return 1

    if setup_other:
        readline.set_completer()
        print("Your database needs to already be configured for "
              "it to work. i.e. the user, password, and database need "
              "to already exist. Please enter the required info below.")
        host = input('hostname [localhost]: ')
        host = host if host else 'localhost'
        user = input('username: ')
        passwd = input('password: ')

    init_config(db_type, file_path, host, user, passwd)


def init_config(db_type, db_file='', db_host='', db_user='', db_pass=''):
    """Create an initial config file."""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    config['DEFAULT'] = {'DatabaseType': db_type}
    config['sqlite']  = {'DatabaseFile': db_file}
    config['other']   = {'DatabaseHost': db_host,
                         'DatabaseUser': db_user,
                         'DatabasePass': db_pass}
    write_config()
    # Make config only accessible to user
    os.chmod(CONFIG_FILE, 0o600)

def write_config():
    """Write the current config to CONFIG_FILE."""
    with open(CONFIG_FILE, 'w') as fout:
        config.write(fout)


###############################################################################
#                                 Completion                                  #
###############################################################################


class tabCompleter(object):
    """
    A tab completer that can either complete from
    the filesystem or from a list.

    Taken from:
        https://gist.github.com/iamatypeofwalrus/5637895
    """

    def _listdir(self, root):
        "List directory 'root' appending the path separator to subdirs."
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _complete_path(self, path=None):
        "Perform completion of filesystem path."
        if not path:
            return os.listdir('.')
        path = os.path.expanduser(path)
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
               for p in os.listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in os.listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def pathCompleter(self, test, state):
        """
        This is the tab completer for systems paths.
        Only tested on *nix systems
        """
        line = readline.get_line_buffer()
        if not line:
            return self._complete_path('.')[state]
        else:
            return self._complete_path(line)[state]

    def createListCompleter(self,ll):
        """
        This is a closure that creates a method that autocompletes from
        the given list.

        Since the autocomplete function can't be given a list to complete from
        a closure is used to create the listCompleter function with a list to complete
        from.
        """
        def listCompleter(text,state):
            line   = readline.get_line_buffer()

            if not line:
                return [c + " " for c in ll][state]

            else:
                return [c + " " for c in ll if c.startswith(line)][state]

        self.listCompleter = listCompleter

