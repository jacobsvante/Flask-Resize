import click
import subprocess as subp

common_args = ['docs', 'docs/_build/html']


@click.group()
def cli():
    pass


@click.command()
@click.option('-p', '--push-tag', help='git push the tag', is_flag=True)
def gittag(push_tag):
    from flask_resize import metadata
    v = metadata.__version__
    retcode = subp.call(['git', 'tag', '-a', '%s' % v, '-m', 'Version %s' % v])
    if push_tag and retcode == 0:
        subp.call(['git', 'push', '--tags'])


@click.command()
def release():
    subp.call(['python', 'setup.py', 'sdist', 'bdist_wheel', 'upload'])


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

    cli.add_command(gittag)
    cli.add_command(release)

    cli()
