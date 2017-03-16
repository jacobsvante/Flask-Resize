import pytest

from flask_resize import _compat, exc, resizing
from flask_resize.cache import RedisCache


@pytest.mark.skipif(
    _compat.redis is None,
    reason="Redis not installed"
)
def test_redis_cache(default_filetarget_options, image1_data):

    options = default_filetarget_options.copy()
    cache_store = RedisCache(key='flask-resize-redis-test')
    cache_store.clear()
    options.update(cache_store=cache_store)
    resize_target = resizing.ResizeTarget(**options)

    assert not cache_store.exists(resize_target.unique_key)

    with pytest.raises(exc.CacheMiss):
        resize_target.get_cached_path()

    resize_target.image_store.save('image.png', image1_data)
    resize_target.generate()

    assert cache_store.exists(resize_target.unique_key) is True
    assert resize_target.get_cached_path() == resize_target.unique_key

    cache_store.remove(resize_target.unique_key)
    assert cache_store.exists(resize_target.unique_key) is False
