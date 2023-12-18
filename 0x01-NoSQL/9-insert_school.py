#!/usr/bin/env python3
""" Module for using PyMongo """


def insert_school(mongo_collection, **kwargs):
    """ Inserts new document in collection based on kwargs """
    obj_id = mongo_collection.insert_one(kwargs)

    return obj_id.inserted_id