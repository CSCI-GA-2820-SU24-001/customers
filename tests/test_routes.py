"""
TestCustomer API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from datetime import date
from urllib.parse import quote_plus
from wsgi import app
from service.common import status
from service.models import db, Customer
from .factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/customers"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomerResource(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create customers
    ############################################################
    def _create_customer(self, count: int = 1) -> list:
        """Factory method to create customers in bulk"""
        customers = []
        for _ in range(count):
            test_customer = CustomerFactory()
            response = self.client.post(BASE_URL, json=test_customer.serialize())

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test customer",
            )
            new_customer = response.get_json()
            test_customer.id = new_customer["id"]
            test_customer.name = new_customer["name"]
            test_customer.address = new_customer["address"]
            test_customer.email = new_customer["email"]
            test_customer.phone_number = new_customer["phone_number"]
            test_customer.member_since = date.fromisoformat(
                new_customer["member_since"]
            )
            customers.append(test_customer)
        return customers

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Customer REST API Service", resp.data)
        # data = resp.get_json()
        # self.assertEqual(data["name"], "Customer Service REST API")

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_create_customer(self):
        """It should Create a new Customer"""
        test_customer = CustomerFactory()
        logging.debug("Test Customer: %s", test_customer.serialize())
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_customer = response.get_json()
        self.assertEqual(new_customer["name"], test_customer.name)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["phone_number"], test_customer.phone_number)
        self.assertEqual(
            new_customer["member_since"], test_customer.member_since.isoformat()
        )

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_customer = response.get_json()
        self.assertEqual(new_customer["name"], test_customer.name)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["phone_number"], test_customer.phone_number)
        self.assertEqual(
            new_customer["member_since"], test_customer.member_since.isoformat()
        )

    def test_read_customer(self):
        """It should read an existing Customer"""
        test_customer = CustomerFactory()
        logging.debug("Test Customer: %s", test_customer.serialize())
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_customer = response.get_json()
        self.assertEqual(new_customer["name"], test_customer.name)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["phone_number"], test_customer.phone_number)
        self.assertEqual(
            new_customer["member_since"], test_customer.member_since.isoformat()
        )
        self.assertEqual(
            new_customer["member_since"], test_customer.member_since.isoformat()
        )

        # Retrieve the newly created customer
        # self.assertEqual(0, new_customer["id"])
        read_response = self.client.get(f"{BASE_URL}/{int(new_customer['id'])}")
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)

        # Validate the data matches
        retrieved_customer = read_response.get_json()
        self.assertEqual(retrieved_customer["name"], test_customer.name)
        self.assertEqual(retrieved_customer["address"], test_customer.address)
        self.assertEqual(retrieved_customer["email"], test_customer.email)
        self.assertEqual(retrieved_customer["phone_number"], test_customer.phone_number)
        self.assertEqual(
            retrieved_customer["member_since"], test_customer.member_since.isoformat()
        )

        response = self.client.get(f"{BASE_URL}/-1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # self.assertIn("Customer with id [-1] not found", response.get_data(as_text=True))

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_customer(self):
        """It should Update an existing Customer"""
        # create a customer to update
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the customer
        new_customer = response.get_json()
        logging.debug(new_customer)
        new_customer["name"] = "Ryan"
        response = self.client.put(
            f"{BASE_URL}/{new_customer['id']}", json=new_customer
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_customer = response.get_json()
        self.assertEqual(updated_customer["name"], "Ryan")

    def test_update_non_existing_customer(self):
        """It should not update a non-existent Customer"""

        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get the new customer ID and increment to create a non-existent ID
        new_customer = response.get_json()
        new_customer_id = new_customer["id"]
        non_existent_id = new_customer_id + 1

        # Attempt to update a non-existent customer
        new_customer["name"] = "Ryan"
        response = self.client.put(f"{BASE_URL}/{non_existent_id}", json=new_customer)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_customer_list(self):
        """It should Get a list of Customers"""
        self._create_customer(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_customer(self):
        """It should Delete a Customer"""
        test_customer = self._create_customer(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_customer(self):
        """It should Delete a Customer even if it doesn't exist"""
        # make sure the customer you are deleting does not exist
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_query_by_name(self):
        """It should Query Customers by name"""
        customers = self._create_customer(5)
        test_name = customers[0].name
        name_count = len(
            [customer for customer in customers if customer.name == test_name]
        )
        response = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["name"], test_name)

    def test_query_by_address(self):
        """It should Query Customers by address"""
        customers = self._create_customer(5)
        test_address = customers[0].address
        address_count = len(
            [customer for customer in customers if customer.address == test_address]
        )
        response = self.client.get(
            BASE_URL, query_string=f"address={quote_plus(test_address)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), address_count)
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["address"], test_address)

    def test_query_by_email(self):
        """It should Query Customers by email"""
        customers = self._create_customer(5)
        test_email = customers[0].email
        email_count = len(
            [customer for customer in customers if customer.email == test_email]
        )
        response = self.client.get(
            BASE_URL, query_string=f"email={quote_plus(test_email)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), email_count)
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["email"], test_email)

    def test_query_by_phone_number(self):
        """It should Query Customers by phone_number"""
        customers = self._create_customer(5)
        test_phone_number = customers[0].phone_number
        phone_number_count = len(
            [
                customer
                for customer in customers
                if customer.phone_number == test_phone_number
            ]
        )
        response = self.client.get(
            BASE_URL, query_string=f"phone_number={quote_plus(test_phone_number)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), phone_number_count)
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["phone_number"], test_phone_number)

    def test_query_by_member_since(self):
        """It should Query Customers by member_since"""
        customers = self._create_customer(5)
        test_member_since = customers[0].member_since
        member_since_count = len(
            [
                customer
                for customer in customers
                if customer.member_since == test_member_since
            ]
        )
        # Convert date to string
        member_since_str = test_member_since.isoformat()
        response = self.client.get(
            BASE_URL, query_string=f"member_since={quote_plus(member_since_str)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), member_since_count)
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["member_since"], member_since_str)

    # ----------------------------------------------------------
    # TEST SUSPEND
    # ----------------------------------------------------------
    def test_suspend_customer(self):
        """It should suspend a customer's account"""
        test_customer = CustomerFactory()
        logging.debug("Test Customer: %s", test_customer.serialize())
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_customer = response.get_json()
        new_customer_id = new_customer["id"]
        print(f"{BASE_URL}/{new_customer_id}/suspend")
        response = self.client.put(f"{BASE_URL}/{new_customer_id}/suspend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f"{BASE_URL}/{new_customer_id}")
        suspended_customer = response.get_json()
        self.assertEqual(suspended_customer["status"], "suspended")


######################################################################
#  T E S T   S A D   P A T H S
######################################################################
class TestSadPaths(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_post_request(self):
        """It should return 405 Method Not Allowed for POST request"""
        resp = self.client.post("/")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = resp.get_json()
        self.assertEqual(
            data["error"],
            "Method not allowed. Please use GET method for this endpoint.",
        )

    def test_put_request(self):
        """It should return 405 Method Not Allowed for PUT request"""
        resp = self.client.put("/")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = resp.get_json()
        self.assertEqual(
            data["error"],
            "Method not allowed. Please use GET method for this endpoint.",
        )

    def test_delete_request(self):
        """It should return 405 Method Not Allowed for DELETE request"""
        resp = self.client.delete("/")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = resp.get_json()
        self.assertEqual(
            data["error"],
            "Method not allowed. Please use GET method for this endpoint.",
        )

    def test_patch_request(self):
        """It should return 405 Method Not Allowed for PATCH request"""
        resp = self.client.patch("/")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = resp.get_json()
        self.assertEqual(
            data["error"],
            "Method not allowed. Please use GET method for this endpoint.",
        )

    def test_suspend_non_existing_customer(self):
        """It should return an error when suspending a customer that does not exist"""
        response = self.client.put("/customers/0/suspend")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        """It should not Delete a Customer with no ID"""
        response = self.client.delete(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_customer_no_content_type(self):
        """It should not Create a Customer with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_wrong_content_type(self):
        """It should not Create a Pet with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_no_data(self):
        """It should not Create a Customer with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
