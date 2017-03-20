import pytest

from multiprocessing.dummy import Pool

import flask_resize
from flask_resize import _compat


@pytest.mark.skipif(
    _compat.redis is None,
    reason="Redis not installed"
)
def test_generate_in_progress(default_filetarget_options, image1_data):
    cache_store = flask_resize.cache.RedisCache(
        key='flask-resize-generate-in-progress-test'
    )
    cache_store.clear()
    options = default_filetarget_options.copy()
    options.update(cache_store=cache_store)

    resize_target = flask_resize.resizing.ResizeTarget(**options)

    # Save original file
    resize_target.image_store.save('image.png', image1_data)

    def run(x):
        resize_target.generate()

    pool = Pool(2)

    with pytest.raises(flask_resize.exc.GenerateInProgress):
        pool.map(run, [None] * 2)
