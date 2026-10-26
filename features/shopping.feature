Feature: Shopping Cart Functionality
  As an authenticated user
  I want to add items to my shopping cart
  So that I can verify and purchase them

  Scenario: Add backpack to shopping cart and verify in cart
    Given I am logged in as "standard_user" with password "secret_sauce"
    When I add "Sauce Labs Backpack" to the cart
    Then the cart badge should display "1"
    When I navigate to the shopping cart
    Then the cart page should display "Sauce Labs Backpack"
