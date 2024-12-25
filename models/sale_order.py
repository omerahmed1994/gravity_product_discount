from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_values(
        self, product_id, quantity, linked_line_id=False,
        no_variant_attribute_values=None, product_custom_attribute_values=None,
        **kwargs
    ):
        """
        Prepares the values for creating a sale order line.
        This method is extended to include the `discount_percentage` from the product
        into the discount field of the order line, if applicable.
        """
        self.ensure_one()  # Ensure the method is called on a single record.
        product = self.env['product.product'].browse(product_id)  # Fetch the product record.
        res = super()._prepare_order_line_values(
            product_id, quantity, linked_line_id, no_variant_attribute_values,
            product_custom_attribute_values, **kwargs
        )
        if product.discount_percentage:
            # If the product has a discount percentage, update the order line values.
            res.update({'discount': product.discount_percentage})
        return res
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_discount(self):
        """
        Updates the discount field on the sale order line when the product is changed.
        If the selected product has a `discount_percentage`, it is applied to the line.
        """
        if self.product_id and self.product_id.discount_percentage:
            # Apply the discount percentage from the product to the sale order line.
            self.discount = self.product_id.discount_percentage
