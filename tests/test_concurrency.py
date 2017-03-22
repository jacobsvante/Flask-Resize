from multiprocessing.dummy import Pool

import pytest

import flask_resize

from .decorators import requires_redis


@requires_redis
def test_generate_in_progress(
    redis_cache,
    resizetarget_opts,
    image1_data,
    image1_name
):
    resizetarget_opts.update(cache_store=redis_cache)

    resize_target = flask_resize.resizing.ResizeTarget(**resizetarget_opts)

    # Save original file
    resize_target.image_store.save(image1_name, image1_data)

    def run(x):
        resize_target.generate()

    pool = Pool(2)

    with pytest.raises(flask_resize.exc.GenerateInProgress):
        pool.map(run, [None] * 2)
