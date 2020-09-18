# -*- coding: utf-8 -*-

{
    'name': 'Shipping',
    'version': '1.0',
    'author': 'Technoindo.com',
    'category': 'Shipping Management',
    'depends': [
        'sale_contract',
        "mining_qaqc",
        "stock",
        "procurement",
        "barge"
    ],
    'data': [
        'views/menu.xml',
        'views/shipping.xml',
        "views/port.xml",
        "views/barge_activity.xml",

        'security/shipping_security.xml',
        'security/ir.model.access.csv',

        "data/shipping_data.xml",
    ],
    'qweb': [
        # 'static/src/xml/cashback_templates.xml',
    ],
    'demo': [
        # 'demo/sale_agent_demo.xml',
    ],
    "installable": True,
	"auto_instal": True,
	"application": True,
}
