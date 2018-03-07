import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run

# The repo's URL
REPO_URL = 'https://github.com/vassily-la/obey09.git'

# Pull down source code with git
def _get_latest_source():
    print("gls-start")
    if exists('.git'):
        # 'git fetch' is like 'git pull'
        # But it doesn't immediately update the live source tree
        print("gls-git")
        run('git fetch')
    else:
        print('gls-clone')
        run(f'git clone {REPO_URL} .')
    # Fabric's local() command runs a command on your local machine
    # It's like a wrapper around subprocess.call, but it's convenient
    # Here, it captures the ID of the current commit on yr machine.
    print("gls-cur-current_commit")
    current_commit = local("git log -n 1 --format=%H", capture=True)
    # Blow away any other changes
    print("gls-reset")
    run(f'git reset --hard {current_commit}')

# Update the virtualenv
def _update_virtualenv():
    print("uv-start")
    if not exists('virtualenv/bin/pip'):
        print("uv-create-venv")
        run('virtualenv --python=/use/bin/python3.6 virtualenv')
    print('uv-run-venv')
    run('./virtualenv/bin/pip install -r reqs.txt')

# Create or update dotenv
def _create_or_update_dotenv():
    print("cud-start")
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    print("cud-cur-contents")
    cur_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in cur_contents:
        print('cud-no-secret-key-in-dotenv. GENERATE!')
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        print("cud-append-secret-key")
        append('.env', f'DJANGO_SECRET_KEY={new_secret}')

def _update_static_files():
    print("upd-static")
    run('./virtualenv/bin/python manage.py collectstatic --noinput')

# Migrate the database
def _update_database():
    print('upd-db')
    run('./virtualenv/bin/python manage.py migrate --noinput')

def deploy():
    # We can get the username and the host like that
    # print(env.user)
    # print(env.host)
    site_folder = "/home/vldo/sites/st01.vassily.pro/"
    # site_folder = f"/home/{env.user}/sites/{env.host}"
    # Run this shell command with 'run'
    # 'mkdir -p' can create directories several levels deep
    # Won't complain if it already exists
    # run(f'mkdir -p {site_folder}')
    # 'cd' is a fabric context manager that says:
    # Run all the dollowing statements inside this workong dir.
    # _(leading underscore) indicates they aren't part of public api
    # print(0)
    print("before wuith cd")
    with cd(site_folder):
        # Pull down source code w/ git. Possible results :
        ## Do a git clone if fresh deployment
        ## Do a git fetch + git reset --hard if a previous version is already there
        print('call gls')
        _get_latest_source()

        # Update the virtualenv
        print('call uv')
        _update_virtualenv()

        # Create a new .env file, if necessary
        print('call cud')
        _create_or_update_dotenv()

        # Update static files
        print('call update-static')
        _update_static_files()

        # Migrate the database, if necessary
        print('call update-db')
        _update_database()
