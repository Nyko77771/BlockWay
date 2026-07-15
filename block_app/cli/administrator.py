# Importing Custom
from block_app.services.database_service import DomainDatabase
from block_app.services.password_service import password_hashing

# Obtaining CLick Package for CLI command creation
import click
from flask.cli import with_appcontext

@click.command('admin-reset')

@with_appcontext
def admin_reset():
    # Setting Database
    database = DomainDatabase()

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
    db_user = database.get_db_user_by_username(username)

    if db_user is None:
        click.echo(f'Username not Found')

    if db_user is not None:

        click.echo(f'Checking Passwords')
        db_salt = db_user.salt
        hashed_given_password = password_hashing(current_password, db_salt)
        db_password = db_user.password
        if hashed_given_password == db_password:
            click.echo('User Verified')
            click.echo('Enter New Password:')
            new_password = click.prompt(
                'New Password:',
                hide_input=True,
                confirmation_prompt=True,
                err=True
            )
            hashed_new_password = password_hashing(new_password, db_salt)
            database.update_db_user_password(db_user, hashed_new_password)

