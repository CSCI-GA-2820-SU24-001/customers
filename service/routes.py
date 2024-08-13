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
from flask_restx import Resource, fields, reqparse, inputs
from service.models import Customer
from service.common import status  # HTTP Status Codes
from . import api


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")


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
        jsonify(error="Method not allowed. Please use GET method for this endpoint."),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Customer",
    {
        "name": fields.String(required=True,
                              description="The name of the Customer"),
        "address": fields.String(required=True,
                                 description="The address of the Customer"),
        "email": fields.String(required=True,
                               description="The email of the Customer"),
        "phone_number": fields.String(required=True,
                                      description="The phone number of the Customer"),
        "member_since": fields.Date(required=True,
                                    description="The date the Customer became a member"),
        "status": fields.String(required=True,
                                description="The status of the Customer (e.g., active, inactive)"),
        # Add additional fields if needed
    }
)


customer_model = api.inherit(
    "CustomerModel",
    create_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)


# query string arguments
customer_args = reqparse.RequestParser()
customer_args.add_argument(
    "name", type=str, location="args", required=False, help="List Customers by name"
)
customer_args.add_argument(
    "address", type=str, location="args", required=False, help="List Customers by address"
)
customer_args.add_argument(
    "email", type=str, location="args", required=False, help="List Customers by email"
)
customer_args.add_argument(
    "phone_number", type=str, location="args", required=False, help="List Customers by phone number"
)
customer_args.add_argument(
    "member_since", type=inputs.date_from_iso8601, location="args", required=False,
    help="List Customers by date of becoming a member"
)
customer_args.add_argument(
    "status", type=str, location="args", required=False, help="List Customers by status",
)


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /customers/{id}
######################################################################
@api.route("/customers/<customer_id>")
@api.param("customer_id", "The Customer identifier")
class CustomerResource(Resource):
    """
    CustomerResource class

    Allows the manipulation of a single Customer
    GET /customer/{id} - Returns a Customer with the id
    PUT /customer/{id} - Update a Customer with the id
    DELETE /customer/{id} -  Deletes a Customer with the id
    """

    # ------------------------------------------------------------------
    # READ A CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("get_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def get(self, customer_id):
        """
        Read a customer
        This endpoint will read a customer based on its id
        """
        app.logger.info("Request to Retrieve a Customer with id [%s]...", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            # abort(status.HTTP_404_NOT_FOUND, f"Customer with id [{customer_id}] not found")
            abort(status.HTTP_404_NOT_FOUND, "404 Not Found")

        app.logger.info("Returning customer: %s", customer.name)
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("update_customers")
    @api.response(404, "Customer not found")
    @api.response(400, "The posted Customer data was not valid")
    @api.expect(customer_model)
    @api.marshal_with(customer_model)
    def put(self, customer_id):
        """
        Update a Customer

        This endpoint will update a Customer based the body that is posted
        """
        app.logger.info("Request to Update a customer with id [%s]", customer_id)
        check_content_type("application/json")

        # Attempt to find the Customer and abort if not found
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )

        # Update the Customer with the new data
        data = request.get_json()
        app.logger.info("Processing: %s", data)
        customer.deserialize(data)

        # Save the updates to the database
        customer.update()

        app.logger.info("Customer with ID: %d updated.", customer.id)
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("delete_customers")
    @api.response(204, "Customer deleted")
    def delete(self, customer_id):
        """Delete customer"""
        app.logger.info("Request to Delete a customer with id [%s]..", customer_id)

        customer = Customer.find(customer_id)
        if customer:
            app.logger.info("Customer with ID: %d found.", customer.id)
            customer.delete()

        app.logger.info("Customer with ID: %d delete complete.", customer_id)
        return {}, status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /customers
######################################################################


@api.route("/customers", strict_slashes=False)
class CustomerCollection(Resource):
    """Handles all interactions with collections of Customers"""

    # ------------------------------------------------------------------
    # LIST ALL CUSTOMERS
    # ------------------------------------------------------------------
    @api.doc("list_customers")
    @api.expect(customer_args, validate=True)
    @api.marshal_list_with(customer_model)
    def get(self):
        """List customers"""
        app.logger.info("Request for customer list")

        customers = []

        args = customer_args.parse_args()

        if args["name"]:
            app.logger.info("Find by name: %s", args["name"])
            customers = Customer.find_by_name(args["name"])
        elif args["address"]:
            app.logger.info("Find by address: %s", args["address"])
            customers = Customer.find_by_address(args["address"])
        elif args["email"]:
            app.logger.info("Find by email: %s", args["email"])
            customers = Customer.find_by_email(args["email"])
        elif args["phone_number"]:
            app.logger.info("Find by phone number: %s", args["phone_number"])
            customers = Customer.find_by_phone(args["phone_number"])
        elif args["member_since"]:
            app.logger.info("Find by member_since: %s", args["member_since"])
            customers = Customer.find_by_member_since(args["member_since"])
        else:
            app.logger.info("Find all")
            customers = Customer.all()

        results = [customer.serialize() for customer in customers]
        app.logger.info("Returning %d customers", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("create_customers")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(customer_model, code=201)
    def post(self):
        """
        Create a Customer
        This endpoint will create a Customer based the data in the body that is posted
        """
        app.logger.info("Request to Create a Customer...")

        customer = Customer()
        app.logger.info("Processing: %s", api.payload)
        customer.deserialize(api.payload)

        # Save the new Customer to the database
        customer.create()
        app.logger.info("Customer with new id [%s] saved!", customer.id)

        # Return the location of the new Customer
        location_url = url_for("customer_resource", customer_id=customer.id, _external=True)
        return (
            customer.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  PATH: /customers/{id}/suspend
######################################################################
@api.route("/customers/<customer_id>/suspend")
@api.param("customer_id", "The Customer identifier")
class SuspendResource(Resource):
    """Suspend actions on a Customer"""

    @api.doc("suspend_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model, code=201)
    def put(self, customer_id):
        """Suspend a customer's account"""
        app.logger.info("Request to suspend a customer with id [%s]..", customer_id)

        customer = Customer.find(customer_id)
        if customer:
            app.logger.info("Customer with ID: %d found.", customer.id)
            customer.status = "suspended"
            customer.update()
        else:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )

        return customer.serialize(), status.HTTP_200_OK


# ######################################################################
# # CREATE A NEW CUSTOMER
# ######################################################################
# @app.route("/customers", methods=["POST"])
# def create_customers():
#     """
#     Create a Customer
#     This endpoint will create a Customer based the data in the body that is posted
#     """
#     app.logger.info("Request to Create a Customer...")
#     check_content_type("application/json")

#     customer = Customer()
#     # Get the data from the request and deserialize it
#     data = request.get_json()
#     app.logger.info("Processing: %s", data)
#     customer.deserialize(data)

#     # Save the new Customer to the database
#     customer.create()
#     app.logger.info("Customer with new id [%s] saved!", customer.id)

#     # Return the location of the new Customer
#     location_url = url_for("get_customer", customer_id=customer.id, _external=True)
#     return (
#         jsonify(customer.serialize()),
#         status.HTTP_201_CREATED,
#         {"Location": location_url},
#     )


# ######################################################################
# # READ A CUSTOMER
# ######################################################################
# @app.route("/customers/<int:customer_id>", methods=["GET"])
# def get_customer(customer_id):
#     """
#     Read a customer
#     This endpoint will read a customer based on its id
#     """
#     app.logger.info("Request to Retrieve a Customer with id [%s]...", customer_id)
#     customer = Customer.find(customer_id)
#     if not customer:
#         abort(status.HTTP_404_NOT_FOUND, f"Customer with id [{customer_id}] not found")

#     app.logger.info("Returning customer: %s", customer.name)
#     return jsonify(customer.serialize()), status.HTTP_200_OK


# ######################################################################
# # UPDATE AN EXISTING CUSTOMER
# ######################################################################
# @app.route("/customers/<int:customer_id>", methods=["PUT"])
# def update_customers(customer_id):
#     """
#     Update a Customer

#     This endpoint will update a Customer based the body that is posted
#     """
#     app.logger.info("Request to Update a customer with id [%s]", customer_id)
#     check_content_type("application/json")

#     # Attempt to find the Customer and abort if not found
#     customer = Customer.find(customer_id)
#     if not customer:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Customer with id '{customer_id}' was not found.",
#         )

#     # Update the Customer with the new data
#     data = request.get_json()
#     app.logger.info("Processing: %s", data)
#     customer.deserialize(data)

#     # Save the updates to the database
#     customer.update()

#     app.logger.info("Customer with ID: %d updated.", customer.id)
#     return jsonify(customer.serialize()), status.HTTP_200_OK


# ############################################################
# # LIST A CUSTOMER
# ############################################################
# @app.route("/customers", methods=["GET"])
# def list_customers():
#     """List customers"""
#     app.logger.info("Request for customer list")

#     customers = []

#     # Parse any arguments from the query string
#     name = request.args.get("name")
#     address = request.args.get("address")
#     email = request.args.get("email")
#     phone_number = request.args.get("phone_number")
#     member_since = request.args.get("member_since")

#     if name:
#         app.logger.info("Find by name: %s", name)
#         customers = Customer.find_by_name(name)
#     elif address:
#         app.logger.info("Find by address: %s", address)
#         customers = Customer.find_by_address(address)
#     elif email:
#         app.logger.info("Find by email: %s", address)
#         customers = Customer.find_by_email(email)
#     elif phone_number:
#         app.logger.info("Find by phone number: %s", phone_number)
#         customers = Customer.find_by_phone(phone_number)
#     elif member_since:
#         app.logger.info("Find by member_since: %s", member_since)
#         # Convert the member_since parameter to a date using fromisoformat
#         member_since_date = date.fromisoformat(member_since)
#         customers = Customer.find_by_member_since(member_since_date)
#     else:
#         app.logger.info("Find all")
#         customers = Customer.all()

#     results = [customer.serialize() for customer in customers]
#     app.logger.info("Returning %d customers", len(results))
#     return jsonify(results), status.HTTP_200_OK


# ############################################################
# # DELETE A CUSTOMER
# ############################################################
# @app.route("/customers/<int:customer_id>", methods=["DELETE"])
# def delete_customers(customer_id):
#     """Delete customer"""
#     app.logger.info("Request to Delete a customer with id [%s]..", customer_id)

#     customer = Customer.find(customer_id)
#     if customer:
#         app.logger.info("Customer with ID: %d found.", customer.id)
#         customer.delete()

#     app.logger.info("Customer with ID: %d delete complete.", customer_id)
#     return {}, status.HTTP_204_NO_CONTENT


# ############################################################
# # SUSPEND A CUSTOMER
# ############################################################
# @app.route("/customers/<int:customer_id>/suspend", methods=["PUT"])
# def suspend_customer(customer_id):
#     """Suspend a customer's account"""
#     app.logger.info("Request to suspend a customer with id [%s]..", customer_id)

#     customer = Customer.find(customer_id)
#     if customer:
#         app.logger.info("Customer with ID: %d found.", customer.id)
#         customer.status = "suspended"
#         customer.update()
#     else:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Customer with id '{customer_id}' was not found.",
#         )

#     return jsonify(customer.serialize()), status.HTTP_200_OK


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
