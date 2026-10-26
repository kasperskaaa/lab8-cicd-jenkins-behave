Feature: User Login
  As a registered user
  I want to log in to the application
  So that I can see the inventory

  Scenario: Successful login with standard user
    Given I open the Swag Labs login page
    When I enter username "standard_user" and password "secret_sauce"
    And I click the login button
    Then I should be redirected to the inventory page
    And the page title should be "Products"

  Scenario: Failed login with locked out user
    Given I open the Swag Labs login page
    When I enter username "locked_out_user" and password "secret_sauce"
    And I click the login button
    Then I should see an error message containing "Sorry, this user has been locked out"

  Scenario: Failed login with invalid password
    Given I open the Swag Labs login page
    When I enter username "standard_user" and password "wrong_password"
    And I click the login button
    Then I should see an error message containing "Username and password do not match any user in this service"
