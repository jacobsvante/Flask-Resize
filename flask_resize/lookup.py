#!-*- coding: utf-8 -*-
"""
:author: Stefan Lehmann
:email: stefan.st.lehmann@gmail.com
:created: 2016

"""
import os
from collections import namedtuple
from sqlitedict import SqliteDict


LookupItem = namedtuple(
    'LookupItem', 'original_path size modified_date')


class Lookup(object):

    def __init__(self, lookup_path):

        self.lookup_path = lookup_path

    def has_image_changed(self, original_path, full_cache_path):

        with SqliteDict(self.lookup_path) as lookup:

            lookup_item = lookup.get(full_cache_path)

            if lookup_item is None:
                return False

            org_size = os.path.getsize(original_path)
            org_modified_date = os.path.getmtime(original_path)

            if (org_size != lookup_item.size or
                    org_modified_date != lookup_item.modified_date):

                return True

    def update(self, original_path, full_cache_path):
        item = LookupItem(
            original_path,
            os.path.getsize(original_path),
            os.path.getmtime(original_path)
        )

        with SqliteDict(self.lookup_path) as lookup:
            lookup[full_cache_path] = item
            lookup.commit()
