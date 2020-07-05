# -*- coding: utf-8 -*-

{
    'name': 'Shipping',
    'version': '1.0',
    'author': 'Technoindo.com',
    'category': 'Shipping Management',
    'depends': [
        'sale_contract',
    ],
    'data': [
        'views/menu.xml',
        'views/shipping.xml',
        'views/barge.xml',
        'security/shipping_security.xml',
        'security/ir.model.access.csv',

    ],
    'qweb': [
        # 'static/src/xml/cashback_templates.xml',
    ],
    'demo': [
        # 'demo/sale_agent_demo.xml',
    ],
    "installable": True,
	"auto_instal": False,
	"application": True,
}
