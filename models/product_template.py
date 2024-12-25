from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Field to store discount percentage
    discount_percentage = fields.Float(string='Discount', default=0.0)
    # Field to store the computed discounted price
    discounted_price = fields.Monetary(string='Discounted Price', compute='_compute_discounted_price')

    # Compute the discounted price based on the discount percentage
    @api.depends('list_price', 'discount_percentage')
    def _compute_discounted_price(self):
        """
        Computes the discounted price for the product based on the list price and discount percentage.
        If no discount is applied, the discounted price equals the list price.
        Note: This calculation is independent of any discounts applied via pricelists.
        """
        for product in self:
            if product.discount_percentage > 0:
                # Calculate discounted price as list price reduced by discount percentage
                product.discounted_price = product.list_price * (1 - product.discount_percentage / 100)
            else:
                # If no discount, set discounted price equal to list price
                product.discounted_price = product.list_price

    def _get_sales_prices(self, pricelist, fiscal_position):
        """
        Overrides the method to adjust the sales prices based on the discount percentage.
        Updates base price and reduced price in the response dictionary.
        
        This method integrates the discount percentage field with the pricelist logic.
        If a discount is applied, it adjusts the reduced price (price_reduce) accordingly.
        """
        res = super()._get_sales_prices(pricelist, fiscal_position)
        for template in self:
            if template.discount_percentage > 0:
                # Set base price and adjust reduced price using the discount percentage
                res[template.id]['base_price'] = res[template.id].get('base_price', res[template.id].get('price_reduce', 0.0))
                res[template.id]['price_reduce'] = res[template.id]['base_price'] * (1 - template.discount_percentage / 100)
        return res

    def _get_additionnal_combination_info(self, product_or_template, quantity, date, website):
        """
        Extends the combination information to include discount details.
        Adds discount percentage, discounted price, and a flag indicating a discount is applied.
        
        Note: This logic ensures that discounts from both the pricelist and the custom 
        discount_percentage field are reflected correctly in the final displayed prices.
        """
        combination_info = super()._get_additionnal_combination_info(product_or_template, quantity, date, website)
        # Include the discount percentage in the combination info
        combination_info['discount_percentage'] = product_or_template.discount_percentage
        if product_or_template.discount_percentage > 0:
            # Indicate that a discounted price is available and update the price
            combination_info['has_discounted_price'] = True
            combination_info['price'] = combination_info['price'] * (1 - product_or_template.discount_percentage / 100)
        return combination_info
