import os

import argh

import flask_resize

config = flask_resize.configuration.Config.from_pyfile(
    os.environ['FLASK_RESIZE_CONF']
)
resize = flask_resize.make_resizer(config)


@argh.named('images')
def clear_images():
    """Delete all generated images from the storage backend"""
    for filepath in resize.storage_backend.delete_tree(
        resize.target_directory
    ):
        yield filepath


@argh.named('cache')
def list_cache():
    """List all items found in cache"""
    for key in resize.cache_store.all():
        yield key


@argh.named('images')
def list_images():
    """List all generated images found in storage backend"""
    for key in resize.storage_backend.list_tree(resize.target_directory):
        yield key


@argh.named('cache')
def sync_cache():
    """
    Syncs paths stored in the cache backend with what's in the storage backend

    Useful when the storage backend destination is shared between multiple
    environments. One use case is when one has synced generated imagery
    from production into one's development environment (for example with
    `aws s3 sync --delete s3://prod-bucket s3://my-dev-bucket`).
    The cache can then be synced with what's been added/removed from the
    bucket `my-dev-bucket`.
    """
    generated_image_paths = set(resize.storage_backend.list_tree(
        resize.target_directory
    ))
    cached_paths = set(resize.cache_store.all())

    for path in (cached_paths - generated_image_paths):
        resize.cache_store.remove(path)
        yield 'Removed {}'.format(path)

    for path in (generated_image_paths - cached_paths):
        resize.cache_store.add(path)
        yield 'Added {}'.format(path)


@argh.named('cache')
def clear_cache():
    """Clear the cache backend from generated images' paths"""
    resize.cache_store.clear()


@argh.named('all')
def clear_all():
    """Clear both the cache and all generated images"""
    clear_cache()
    for filepath in clear_images():
        yield filepath


@argh.arg('-f', '--format')
@argh.arg('-F', '--fill')
def generate(
    filename,
    dimensions=None,
    format=None,
    quality=80,
    fill=False,
    bgcolor=None,
    upscale=True,
    progressive=True,
    placeholder=False
):
    """
    Generate images passed in through stdin. Return URL for resulting image

    Useful to generate images outside of the regular request/response cycle
    of a web app = happier visitors who don't have to wait until image
    processing by Flask-Resize completes. Care has to be taken so that the
    exact same arguments are passed in as what is specified in
    code/templates - the smallest difference in passed in options will cause
    flask resize to generate a new image.

    Use GNU Parallel or similar tool to parallelize the generation
    """
    return resize(
        filename,
        dimensions=dimensions,
        format=format,
        quality=quality,
        fill=fill,
        bgcolor=bgcolor,
        upscale=upscale,
        progressive=progressive,
        placeholder=placeholder,
    )


parser = argh.ArghParser()

argh.add_commands(parser, [generate])

argh.add_commands(
    parser,
    [list_cache, list_images],
    namespace='list',
    title="Commands for listing images and cache",
)
argh.add_commands(
    parser,
    [sync_cache],
    namespace='sync',
    title="Commands for syncing data",
)
argh.add_commands(
    parser,
    [clear_cache, clear_images, clear_all],
    namespace='clear',
    title="Commands for clearing/deleting images and cache",
)
