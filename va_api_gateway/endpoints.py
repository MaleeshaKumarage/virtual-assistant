from app import Resource, request
import redis
import os
import logging
from models import CustomActionsModel
import json

# Set logger
logger = logging.getLogger('flask.app')
logging.basicConfig(level=logging.DEBUG)


# Init model classes

CustomActionsModel = CustomActionsModel()

# Initiate redis
try:
    r = redis.Redis(host=os.environ['REDIS_URL'], port=os.environ['REDIS_PORT'], charset="utf-8", decode_responses=True)
    logger.info("Trying to connect to Redis Docker container ")
except KeyError:
    logger.debug("Local run connecting to Redis  ")
    r = redis.Redis(host='localhost', port=6379, charset="utf-8", decode_responses=True)


class CustomActionsAPI(Resource):

    def get(self):

        # check if result can be served from cache
        if r.exists("all_custom_actions"):
            return json.loads(r.get("all_custom_actions"))

        else:
            # Get results and update the cache with new values
            logging.debug('getting Data from DB')

            result = CustomActionsModel.get_all_custom_actions()
            r.set("all_custom_actions", json.dumps(result), ex=60)

            return result

    def post(self):
        json_data = request.get_json(force=True)
        result = CustomActionsModel.create_action(json_data)

        # Clear redis cache
        r.delete("all_custom_actions")
        return result

    def put(self):

        # Updating record
        json_data = request.get_json(force=True)
        result = CustomActionsModel.update_action(json_data)

        # Clear redis cache
        r.delete("all_custom_actions")
        return result

    def delete(self):
        # Deleting record
        object_id = request.get_json()
        result = CustomActionsModel.delete_action(object_id)

        # Clear redis cache
        r.delete("all_custom_actions")
        return result


