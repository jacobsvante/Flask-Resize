import click
import subprocess as subp

common_args = ['docs', 'docs/_build/html']


@click.group()
def cli():
    pass


@click.group(name='docs', chain=True)
def docs():
    pass


@click.command()
def clean():
    subp.call(['rm', '-rf', 'docs/_build'])


@click.command()
def build():
    subp.call(['sphinx-build'] + common_args)


@click.command()
def serve():
    subp.call(['sphinx-autobuild', '-z', 'flask_resize'] + common_args)


if __name__ == '__main__':
    docs.add_command(clean)
    docs.add_command(build)
    docs.add_command(serve)
    cli.add_command(docs)
    cli()
