from pymongo import MongoClient
from typing import Optional
from .models import Soldier, SoldierCreate, SoldierUpdate, ResponseMessage
import logging

# Configuring logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SoldierDal:
    """Data Access Layer for Soldier operation with MongoDB (synchronous, PyMongo)"""

    def __init__(self, connection_string: str = "mongodb://localhost:27017"):
        "Initialize DAL with MongoDB connection"
        self.client: MongoClient = MongoClient(connection_string)
        self.db = self.client.enemy_soldiers
        self.collection = self.db.soldier_details

    def connect(self) -> bool:
        "Test database connection"
        try:
            self.client.admin.command("ping")
            logger.info("Successfuly connected to MongoDB!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False

    def close(self) -> None:
        "Close database connection"
        self.client.close()

    def get_all_soldiers(self) -> ResponseMessage:
        "Read all soldiers from database"
        try:
            cursor = self.collection.find({})
            soldiers = []
            for document in cursor:
                # Drop Mongo's ObjectId to keep JSON serializable and preserve numeric id
                if "_id" in document:
                    document.pop("_id", None)
                soldiers.append(document)

            logger.info(f"Successfully got {len(soldiers)} soldiers.")
            return ResponseMessage(
                message=f"Successfully got {len(soldiers)} soldiers.",
                success=True,
                data={"soldiers": soldiers},
            )
        except Exception as e:
            logger.error(f"Error getting soldiers: {e}")
            return ResponseMessage(
                message=f"Failed to get soldiers: {str(e)}", success=False
            )

    def create_soldier(self, soldier_data: SoldierCreate) -> ResponseMessage:
        "Create a new soldier record"
        try:
            last_soldier = self.collection.find_one(sort=[("id", -1)])
            new_id = 1 if not last_soldier else last_soldier.get("id", 0) + 1

            soldier_doc = {
                "id": new_id,
                "first_name": soldier_data.first_name,
                "last_name": soldier_data.last_name,
                "phone_number": soldier_data.phone_number,
                "rank": soldier_data.rank,
            }

            result = self.collection.insert_one(soldier_doc)

            if result.inserted_id:
                logger.info(f"Successfully created soldier with ID: {new_id}")
                # PyMongo mutates the original dict and injects _id (ObjectId). Drop it for JSON safety.
                safe_doc = dict(soldier_doc)
                safe_doc.pop("_id", None)
                return ResponseMessage(
                    message=f"Successfully created soldier with ID: {new_id}",
                    success=True,
                    data={"id": new_id, "soldier": safe_doc},
                )
            else:
                return ResponseMessage(message="Failed to create soldier", success=False)
        except Exception as e:
            logger.error(f"Error creating soldier: {e}")
            return ResponseMessage(
                message=f"Failed to create soldier: {str(e)}", success=False
            )

    def update_soldier(
        self, soldier_id: int, update_data: SoldierUpdate
    ) -> ResponseMessage:
        "Update soldier record by ID"
        try:
            update_doc = {}
            if update_data.first_name is not None:
                update_doc["first_name"] = update_data.first_name
            if update_data.last_name is not None:
                update_doc["last_name"] = update_data.last_name
            if update_data.phone_number is not None:
                update_doc["phone_number"] = update_data.phone_number
            if update_data.rank is not None:
                update_doc["rank"] = update_data.rank

            if not update_doc:
                return ResponseMessage(message="No fields to update", success=False)

            result = self.collection.update_one({"id": soldier_id}, {"$set": update_doc})

            if result.matched_count == 0:
                return ResponseMessage(
                    message=f"Soldier with ID {soldier_id} not found", success=False
                )

            if result.modified_count > 0:
                logger.info(f"Successfully updated soldier with ID: {soldier_id}")
                return ResponseMessage(
                    message=f"Successfully updated soldier with ID: {soldier_id}",
                    success=True,
                    data={"id": soldier_id, "updated_fields": update_doc},
                )
            else:
                return ResponseMessage(
                    message=f"Soldier with ID {soldier_id} found but no changes made",
                    success=True,
                )
        except Exception as e:
            logger.error(f"Error updating soldier {soldier_id}: {e}")
            return ResponseMessage(
                message=f"Failed to update soldier: {str(e)}", success=False
            )

    def delete_soldier(self, soldier_id: int) -> ResponseMessage:
        "Delete a soldier record by ID"
        try:
            result = self.collection.delete_one({"id": soldier_id})

            if result.deleted_count == 0:
                return ResponseMessage(
                    message=f"Soldier with ID {soldier_id} not found", success=False
                )

            logger.info(f"Successfully deleted soldier with ID: {soldier_id}")
            return ResponseMessage(
                message=f"Successfully deleted soldier with ID: {soldier_id}",
                success=True,
                data={"id": soldier_id},
            )
        except Exception as e:
            logger.error(f"Error deleting soldier {soldier_id}: {e}")
            return ResponseMessage(
                message=f"Failed to delete soldier: {str(e)}", success=False
            )

    def get_soldier_by_id(self, soldier_id: int) -> ResponseMessage:
        "Get a specific soldier by ID"
        try:
            soldier = self.collection.find_one({"id": soldier_id})

            if not soldier:
                return ResponseMessage(
                    message=f"Soldier with ID {soldier_id} not found", success=False
                )

            # Drop Mongo's ObjectId field before returning
            if "_id" in soldier:
                soldier.pop("_id", None)

            logger.info(f"Successfully got soldier with ID: {soldier_id}")
            return ResponseMessage(
                message=f"Successfully got soldier with ID: {soldier_id}",
                success=True,
                data={"soldier": soldier},
            )
        except Exception as e:
            logger.error(f"Error getting soldier {soldier_id}: {e}")
            return ResponseMessage(
                message=f"Failed to get soldier: {str(e)}", success=False
            )