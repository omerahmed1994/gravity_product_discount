Product Discount Feature for Odoo eCommerce

Overview
This Odoo module introduces a simple yet powerful feature that enables administrators to apply percentage-based discounts to specific products in the eCommerce module. The discounted price is seamlessly reflected across the product listing, detail pages, cart, and checkout processes.

Features
Admin Control for Discounts:

Adds a new field, Discount Percentage, to the product form in the backend (product.template model).
Allows administrators to set a percentage discount for individual products.
Automatically calculates the discounted price based on the original product price and the specified discount percentage.
Dynamic Pricing in the Store:

Displays the discounted price (if applicable) alongside the original price in the eCommerce product listings and detail pages.
Applies a "strikethrough" effect to the original price when a discount is active, clearly highlighting the savings for customers.
Ensures non-discounted products are displayed with their regular pricing.
Cart and Checkout Integration:

Reflects the correct discounted price when products are added to the cart.
Ensures the discount is applied consistently during the checkout process.
Updates the final invoice to include the discounted price, offering transparency for customers.
Seamless User Experience:

The feature is designed to integrate naturally into Odoo’s eCommerce module, offering a clean and intuitive interface for both administrators and customers.

Designed for Odoo 17

Installation

Download and install the module through the Odoo Apps interface.
Activate developer mode to access the technical features if necessary.
Navigate to the Products section in the backend and set the discount percentage for desired products.

Usage
Open the product form view in the backend and set a discount percentage.
Visit the eCommerce store to see the updated pricing.
Add discounted products to the cart and proceed to checkout to verify the applied discount.
