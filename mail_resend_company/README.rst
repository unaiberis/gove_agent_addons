.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Company Resend Mail
===================


Features
========

### Email Resend Functionality for `Surflogic`

This module includes a specific functionality to resend emails containing the subject `'Surflogic Pedido (Ref PVS'`. The functionality is activated under the following conditions:

- **Conditions for Resending:**
  - The `resend_mail` option must be enabled in the company configuration (`self.env.company`).
  - The email model (`mail.model`) must be `"sale.order"`.
  - The email subject (`mail.subject`) must contain `"Surflogic"`.

- **Resending Process:**
  - If the email does not already include the recipient `'info@surflogic.com'`, it will be added as an additional recipient.
  - The email entry in the recipient list (`email_list`) is duplicated to ensure that `'info@surflogic.com'` receives the email.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/avanzosc/odoo-addons/issues>`_. In case of trouble, please check there if your issue has already been reported. If you spotted it first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------
* Ana Juaristi <anajuaristi@avanzosc.es>
* Unai Beristain <unaiberistain@avanzosc.es>

Do not contact contributors directly about support or help with technical issues.
