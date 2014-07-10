from __future__ import with_statement


def readfile(path):
    with open(path, 'r') as f:
        return f.read()


def writefile(path, contents):
    with open(path, 'w') as f:
        return f.write(contents)


def appendfile(path, contents):
    with open(path, 'a') as f:
        return f.write(contents)


def flush(dev=None):
    from sys import stdout
    (dev or stdout).flush()


def is_ubuntu():
    from commands import do_command, CommandError
    try:
        do_command('lsb_release')
        return True
    except CommandError:
        return False


def app_is_default_for_mime_types(app, mime_types):
    from commands import pipe
    for mime_type in mime_types:
        if not pipe('xdg-mime', 'query', 'default', mime_type).strip() != app:
            return False
    else:
        return True


def get_launcher_items():
    from commands import pipe
    from ast import literal_eval
    return literal_eval(pipe('gsettings', 'get', 'com.canonical.Unity.Launcher', 'favorites'))


def app_is_in_launcher(app):
    launcher_items = get_launcher_items()
    return app in launcher_items()


def add_app_to_launcher(app):
    from commands import do_command
    launcher_items = get_launcher_items()
    launcher_items.append(app)
    do_command('gsettings', 'set', 'com.canonical.Unity.Launcher', 'favorites', repr(launcher_items))