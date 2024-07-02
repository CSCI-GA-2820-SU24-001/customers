######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Customer Store Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Customers from the inventory of customers in the CustomerShop
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Customer
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
# @app.route("/")
# def index():
#     """Root URL response"""
#     app.logger.info("Request for Root URL")
#     return (
#         jsonify(
#             name="Customer Service REST API",
#             version="1.0",
#             paths=url_for("list_customers", _external=True),
#         ),
#         status.HTTP_200_OK,
#     )


@app.route("/", methods=["GET"])
def get_service_info():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Customer Service REST API",
            version="1.0",
            paths=url_for("list_customers", _external=True),
        ),
        status.HTTP_200_OK,
    )


@app.route("/", methods=["POST", "PUT", "DELETE", "PATCH"])
def handle_root_non_get_requests():
    """Handle non-GET requests to the root URL"""
    app.logger.info("Non-GET request for Root URL")
    return (
        jsonify(
            error="Method not allowed. Please use GET method for this endpoint."
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW CUSTOMER
######################################################################
@app.route("/customers", methods=["POST"])
def create_customers():
    """
    Create a Customer
    This endpoint will create a Customer based the data in the body that is posted
    """
    app.logger.info("Request to Create a Customer...")
    check_content_type("application/json")

    customer = Customer()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    customer.deserialize(data)

    # Save the new Customer to the database
    customer.create()
    app.logger.info("Customer with new id [%s] saved!", customer.id)

    # Return the location of the new Customer
    # TODO: uncomment this code when get_customers is implemented
    # location_url = url_for("get_customers", customer_id=customer.id, _external=True)
    location_url = "unknown"
    return jsonify(customer.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# READ A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    """
    Read a customer
    This endpoint will read a customer based on its id
    """
    app.logger.info("Request to Retrieve a Customer with id [%s]...", customer_id)
    customer = Customer.find(customer_id)
    if not customer:
        abort(status.HTTP_404_NOT_FOUND, f"Customer with id [{customer_id}] not found")

    app.logger.info("Returning customer: %s", customer.name)
    return jsonify(customer.serialize()), status.HTTP_200_OK


############################################################
# LIST A CUSTOMER
############################################################
@app.route("/customers", methods=["GET"])
def list_customers():
    """List customers"""
    app.logger.info("Request for customer list")
    customers = []

    customers = Customer.all()

    if not customers:
        abort(status.HTTP_404_NOT_FOUND, "No customers found.")

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(customers))
    return jsonify(results), status.HTTP_200_OK


############################################################
# DELETE A CUSTOMER
############################################################
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customers(customer_id):
    """Delete customer"""
    app.logger.info("Request to Delete a customer with id [%s]..", customer_id)

    customer = Customer.find(customer_id)
    if customer:
        app.logger.info("Customer with ID: %d found.", customer.id)
        customer.delete()

    app.logger.info("Customer with ID: %d delete complete.", customer_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# Checks the ContentType of a request
######################################################################


def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
