"""
Customer Steps

Steps file for customers.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""

import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following customers")
def step_impl(context):
    """Delete all Customers and load new ones"""

    # Get a list all of the customers
    rest_endpoint = f"{context.base_url}/api/customers"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for pet in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{pet['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new pets
    for row in context.table:
        payload = {
            "name": row["name"],
            "address": row["address"],
            "email": row["email"],
            "phone_number": row["phone_number"],
            "member_since": row["member_since"],
            "status": row["status"],
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
