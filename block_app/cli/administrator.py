import click
from flask.cli import with_appcontext

@click.command('admin-reset')
@with_appcontext
def admin_reset():
    print('Please provide your username')
    username = click.prompt('Username:')
    print('Type in your password')
    current_password = click.prompt(
        'Password:',
        hide_input=True,
        confirmation_prompt=True,
        err=True
    )
    click.echo(f'Checking {username}')

