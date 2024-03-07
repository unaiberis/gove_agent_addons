# Copyright 2024 Unai Beristain - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Gove Agent Choose Customer Website Sale",
    "summary": "Assign agent customer to cart in checkout process and more personalizations",
    "category": "Website",
    "version": "14.0.1.1.0",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "license": "AGPL-3",
    "depends": [
        "portal",
        "sale",
        "sale_commission",
        "sale_commission_group",
        "website_sale",
        "website_sale_multiple_coupon",
        "website_sale_checkout_extra_fields",
        "website_sale_assign_agent_customer",
        "woo_commerce_ept",
    ],
    "data": [
        "views/assets.xml",
        "views/website_sale.xml",
        "views/website_front_page.xml",
        "views/my_account_page_remove_links.xml",
        "views/show_draft_finished_column.xml",
#         "views/action_server_base_automation.xml",


    ],
    "installable": True,
}
