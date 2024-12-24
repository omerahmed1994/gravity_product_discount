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
        for product in self:
            if product.discount_percentage > 0:
                product.discounted_price = product.list_price * (1 - product.discount_percentage / 100)
            else:
                product.discounted_price = product.list_price

    def _get_sales_prices(self, pricelist, fiscal_position):
        res = super()._get_sales_prices(pricelist, fiscal_position)
        for template in self:
            if template.discount_percentage > 0:
                res[template.id]['base_price'] = res[template.id].get('base_price', res[template.id].get('price_reduce', 0.0))
                res[template.id]['price_reduce'] = res[template.id]['base_price'] * (1 - template.discount_percentage / 100)
        return res
    
    def _get_additionnal_combination_info(self, product_or_template, quantity, date, website):
        """Computes additional combination info, based on given parameters

        :param product_or_template: `product.product` or `product.template` record
            as variant values must take precedence over template values (when we have a variant)
        :param float quantity:
        :param date date: today's date, avoids useless calls to today/context_today and harmonize
            behavior
        :param website: `website` record holding the current website of the request (if any),
            or the contextual website (tests, ...)
        :returns: additional product/template information
        :rtype: dict
        """
        pricelist = website.pricelist_id
        currency = website.currency_id

        compare_list_price = product_or_template.compare_list_price
        list_price = product_or_template._price_compute('list_price')[product_or_template.id]
        price_extra = product_or_template._get_attributes_extra_price()
        if product_or_template.currency_id != currency:
            price_extra = self.currency_id._convert(
                from_amount=price_extra,
                to_currency=currency,
                company=self.env.company,
                date=date,
            )
            list_price = self.currency_id._convert(
                from_amount=list_price,
                to_currency=currency,
                company=self.env.company,
                date=date,
            )
            compare_list_price = product_or_template.currency_id._convert(
                from_amount=compare_list_price,
                to_currency=self.currency_id,
                company=self.env.company,
                date=date,
                round=False)

        # Pricelist price doesn't have to be converted
        pricelist_price = pricelist._get_product_price(
            product=product_or_template,
            quantity=quantity,
            target_currency=currency,
        )

        if pricelist.discount_policy == 'without_discount':
            has_discounted_price = currency.compare_amounts(list_price, pricelist_price) == 1
        else:
            has_discounted_price = False

        combination_info = {
            'price_extra': price_extra,
            'price': pricelist_price,
            'list_price': list_price,
            'has_discounted_price': has_discounted_price,
            'compare_list_price': compare_list_price,
        }

        # Apply taxes
        fiscal_position = website.fiscal_position_id.sudo()


        product_taxes = product_or_template.sudo().taxes_id.filtered(
            lambda t: t.company_id == self.env.company)
        taxes = self.env['account.tax']
        if product_taxes:
            taxes = fiscal_position.map_tax(product_taxes)
            # We do not apply taxes on the compare_list_price value because it's meant to be
            # a strict value displayed as is.
            for price_key in ('price', 'list_price', 'price_extra'):
                combination_info[price_key] = self._apply_taxes_to_price(
                    combination_info[price_key],
                    currency,
                    product_taxes,
                    taxes,
                    product_or_template,
                )

        combination_info.update({
            'prevent_zero_price_sale': website.prevent_zero_price_sale and float_is_zero(
                combination_info['price'],
                precision_rounding=currency.rounding,
            ),

            'base_unit_name': product_or_template.base_unit_name,
            'base_unit_price': product_or_template._get_base_unit_price(combination_info['price']),

            # additional info to simplify overrides
            'currency': currency,  # displayed currency
            'date': date,
            'product_taxes': product_taxes,  # taxes before fpos mapping
            'taxes': taxes,  # taxes after fpos mapping
        })

        if pricelist.discount_policy != 'without_discount':
            # Leftover from before cleanup, different behavior between ecommerce & backend configurator
            # probably to keep product sales price hidden from customers ?
            combination_info['list_price'] = combination_info['price']

        if website.is_view_active('website_sale.product_tags') and product_or_template.is_product_variant:
            combination_info['product_tags'] = self.env['ir.ui.view']._render_template(
                'website_sale.product_tags', values={
                    'all_product_tags': product_or_template.all_product_tag_ids.filtered('visible_on_ecommerce')
                }
            )

        return combination_info
