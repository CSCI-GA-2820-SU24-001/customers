Feature: The pet store service back-end
    As a Pet Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my pets

Background:
    Given the following customers
      | name       | address                  | email                 | phone_number  | member_since | status   |
      | Fluffy     | 123 Pet Lane, Dogtown    | fluffy@example.com    | 555-1234      | 2021-05-12   | active   |
      | Whiskers   | 456 Cat St, Meow City    | whiskers@example.com  | 555-5678      | 2020-11-23   | suspended|
      | Rex        | 789 Woof Blvd, Barkburg  | rex@example.com       | 555-9876      | 2019-07-01   | active   |
      | Tweety     | 321 Bird Ave, Aviary     | tweety@example.com    | 555-6543      | 2022-02-18   | active   |


Scenario: The server is running
    When I visit the "home page"
    Then I should see "Customer RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
    When I visit the "Home Page"
    And I set the "Name" to "Sai"
    And I set the "Address" to "80 Court House"
    And I set the "Email" to "sb@nyu.edu"
    And I set the "Phone" to "5512298011"
    And I set the "Since" to "06-16-2022"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Address" field should be empty
    And the "Email" field should be empty
    And the "Phone" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Sai" in the "Name" field
    And I should see "80 Court House" in the "Address" field
    And I should see "sb@nyu.edu" in the "Email" field
    And I should see "5512298011" in the "Phone" field
    And I should see "2022-06-16" in the "Since" field

Scenario: Update a Customer
    When I visit the "Home Page"
    And I set the "Name" to "Fluffy"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Fluffy" in the "Name" field
    And I should see "123 Pet Lane, Dogtown" in the "Address" field
    And I should see "fluffy@example.com" in the "Email" field
    And I should see "555-1234" in the "Phone" field
    And I should see "2021-05-12" in the "Since" field
    When I change "Name" to "Loki"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Loki" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Loki" in the results
    And I should not see "Fluffy" in the results

Scenario: Delete a Customer
    When I visit the "Home Page"
    And I set the "Name" to "Fluffy"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Fluffy" in the "Name" field
    And I should see "123 Pet Lane, Dogtown" in the "Address" field
    And I should see "fluffy@example.com" in the "Email" field
    And I should see "555-1234" in the "Phone" field
    And I should see "2021-05-12" in the "Since" field
    When I change "Name" to "Fluffy"
    And I press the "Delete" button
    Then I should see the message "Customer has been Deleted!"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found"

Scenario: Read a Customer
    When I visit the "Home Page"
    And I set the "Name" to "Sai"
    And I set the "Address" to "80 Court House"
    And I set the "Email" to "sb@nyu.edu"
    And I set the "Phone" to "5512298011"
    And I set the "Since" to "06-16-2022"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Sai" in the "Name" field
    And I should see "80 Court House" in the "Address" field
    And I should see "sb@nyu.edu" in the "Email" field
    And I should see "5512298011" in the "Phone" field
    And I should see "2022-06-16" in the "Since" field

Scenario: List all Customers
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Fluffy" in the results
    And I should see "Whiskers" in the results
    And I should see "Rex" in the results
    And I should see "Tweety" in the results

Scenario: Query a Customer by Member Since
    When I visit the "Home Page"
    And I set the "Since" to "11-23-2020"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Whiskers" in the "Name" field
    And I should see "456 Cat St, Meow City" in the "Address" field

Scenario: Query a Customer by Phone No
    When I visit the "Home Page"
    And I set the "Phone" to "555-9876"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Rex" in the "Name" field
    And I should see "555-9876" in the "Phone" field

Scenario: Suspend a customer by Customer Id
    When I visit the "Home Page"
    And I set the "Name" to "Rex"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "789 Woof Blvd, Barkburg" in the "Address" field
    And I should see "rex@example.com" in the "Email" field
    And I should see "555-9876" in the "Phone" field
    And I should see "2019-07-01" in the "Since" field
    When I press the "Suspend" button
    Then I should see the message "Customer has been Suspended!"
    When I press the "Retrieve" button
