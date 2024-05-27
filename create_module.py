import os

module_name = "company_resend_email"
module_path = os.path.join(os.getcwd(), module_name)

# Define the structure and content of the files
files_structure = {
    "__init__.py": "",
    "__manifest__.py": f"""\
{{
    'name': 'Company Resend Email',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'Adds a resend_email field to the company model',
    'description': 'This module adds a unique resend_email field to each company in Odoo.',
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': False,
}}
""",
    "models/__init__.py": "from . import res_company",
    "models/res_company.py": """\
from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    resend_email = fields.Boolean(string='Resend Email', default=False)

    @api.multi
    def toggle_resend_email(self):
        self.ensure_one()
        self.resend_email = not self.resend_email
""",
    "views/res_company_views.xml": """\
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="view_res_company_form" model="ir.ui.view">
        <field name="name">res.company.form</field>
        <field name="model">res.company</field>
        <field name="inherit_id" ref="base.view_company_form"/>
        <field name="arch" type="xml">
            <xpath expr="//sheet" position="inside">
                <group>
                    <field name="resend_email"/>
                    <button name="toggle_resend_email" type="object" string="Toggle Resend Email" class="oe_highlight"/>
                </group>
            </xpath>
        </field>
    </record>
</odoo>
"""
}

# Create directories and files
os.makedirs(os.path.join(module_path, "models"), exist_ok=True)
os.makedirs(os.path.join(module_path, "views"), exist_ok=True)

for file_path, file_content in files_structure.items():
    full_path = os.path.join(module_path, file_path)
    with open(full_path, "w") as f:
        f.write(file_content)

print(f"Module {module_name} created successfully in {module_path}")
