import pytest

from flask_resize import exc, resizing

from .decorators import requires_redis


@requires_redis
def test_redis_cache(redis_cache, resizetarget_opts, image1_data, image1_name):

    resizetarget_opts.update(cache_store=redis_cache)
    resize_target = resizing.ResizeTarget(**resizetarget_opts)

    assert not redis_cache.exists(resize_target.unique_key)

    with pytest.raises(exc.CacheMiss):
        resize_target.get_cached_path()

    resize_target.image_store.save(image1_name, image1_data)
    resize_target.generate()

    assert redis_cache.exists(resize_target.unique_key) is True
    assert resize_target.get_cached_path() == resize_target.unique_key

    redis_cache.remove(resize_target.unique_key)
    assert redis_cache.exists(resize_target.unique_key) is False
