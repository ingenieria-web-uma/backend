from bson import ObjectId


class MongoBase:
    def to_mongo_dict(self, exclude_none: bool = False):
        # get fields that are type PydanticObjectId and convert them to ObjectId
        data = self.__dict__.copy()
        for key, value in list(data.items()):
            if isinstance(value, ObjectId):
                data[key] = ObjectId(str(value))
            if exclude_none:
                if value is None:
                    del data[key]
        return data
