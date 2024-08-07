"""
Models for Customer

All of the models are stored in this module
"""
import os
import logging
from datetime import date
from flask_sqlalchemy import SQLAlchemy

# global variables for retry as discussed in lab
RETRY_COUNT = int(os.environ.get("RETRY_COUNT", 5))
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", 1))
RETRY_BACKOFF = int(os.environ.get("RETRY_BACKOFF", 2))

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Customer(db.Model):
    """
    Class that represents a Customer
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(63), nullable=False)
    phone_number = db.Column(db.String(32), nullable=False)
    member_since = db.Column(db.Date(), nullable=False, default=date.today())
    # Database auditing fields
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    last_updated = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False
    )
    status = db.Column(db.String(20), nullable=False, default="active")

    def __repr__(self):
        return f"<Customer {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Customer to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self) -> None:
        """
        Updates a Customer to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Customer from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "email": self.email,
            "phone_number": self.phone_number,
            "member_since": self.member_since.isoformat(),
            "status": self.status,
        }

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.address = data["address"]
            self.email = data["email"]
            self.phone_number = data["phone_number"]
            self.member_since = date.fromisoformat(data["member_since"])
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Customer: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Customers in the database"""
        logger.info("Processing all Customers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Customer by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Customers with the given name

        Args:
            name (string): the name of the Customers you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_address(cls, address):
        """Returns all Customers with the given address

        Args:
            name (string): the address of the Customers you want to match
        """
        logger.info("Processing address query for %s ...", address)
        return cls.query.filter(cls.address == address)

    @classmethod
    def find_by_email(cls, email):
        """Returns all Customers with the given email

        Args:
            name (string): the email of the Customers you want to match
        """
        logger.info("Processing address query for %s ...", email)
        return cls.query.filter(cls.email == email)

    @classmethod
    def find_by_phone(cls, phone_number):
        """Returns all Customers with the given phone number

        Args:
            name (string): the phone number of the Customers you want to match
        """
        logger.info("Processing phone query for %s ...", phone_number)
        return cls.query.filter(cls.phone_number == phone_number)

    @classmethod
    def find_by_member_since(cls, member_since):
        """Returns all Customers with the given membership date

        Args:
            name (string): the date of the Customers you want to match
        """
        logger.info("Processing address query for %s ...", member_since)
        return cls.query.filter(cls.member_since == member_since)
