# Customers API

[![Build Status](https://github.com/CSCI-GA-2820-SU24-001/customers/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU24-001/customers/actions)
[![codecov](https://codecov.io/github/CSCI-GA-2820-SU24-001/customers/graph/badge.svg?token=284AWMT30I)](https://codecov.io/github/CSCI-GA-2820-SU24-001/customers)

## Introduction
This is the RESTful API for manageing customers. It allows you to create, retrieve, update, and delete customers.

## Getting Started
Clone this repository and open the folder in a container. 

## API Endpoints

### POST /customers
- **Method:** POST
- **Description:** Creates a customer.

### GET /customers/<int:customer_id>
- **Method:** GET
- **Description:** Read an existing customer with specific customer ID.

### PUT /customers/<int:customer_id>
- **Method:** PUT
- **Description:** Update an existing customer.

### GET /customers
- **Method:** GET
- **Description:** List existing customers and query customer attributes like name, email, address, phone number and member since

### DELETE /customers/<int:customer_id>
- **Method:** DELETE
- **Description:** Delete an existing customer with specific customer ID.

### PUT /customers/<int:customer_id>/suspend
- **Method:** PUT
- **Description:** Suspend an existing customer with specific customer ID.

## Error Handling
The API returns a JSON object with a status code and a string message when an error occurs. For example, `{ status.HTTP_404_NOT_FOUND, f"Customer with id '{customer_id}' was not found.", }`.

## Testing
Run 'make test' to execute the test suite.

## Kubernetes
- **Delete cluster:** make cluster-rm
- **Create cluster:** make cluster
- **Build the docker image:** docker build -t customers:latest .
- **Create tag for image:** docker tag customers:latest cluster-registry:5000/customers:latest
- **Push the docker image:** docker push cluster-registry:5000/customers:latest
- **Apply Kubernetes:** kc apply -f k8s/ or alternatively, make deploy 