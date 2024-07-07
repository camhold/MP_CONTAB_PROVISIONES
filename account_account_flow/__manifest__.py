{
    'name': "Account Account Flow",
    'description': """
        Se genera el flujo de contabilidad
    """,

    'author': "Tonny Velazquez Juarez",
    'website': "corner.store59@gmail.com",

    'category': 'account_payment_flow',
    "version": '15.0.1.0.0',
    'depends': ['account', 'payroll_payment'],
    'data': [
        'security/ir.model.access.csv',
        'data/mp_provision_secuence.xml',
        # 'data/mp_provision_account_move_secuence.xml',
        'views/account_payment_flow_view.xml',
        'views/account_account_type_views.xml',
        'views/account_mp_provision_account_move.xml',
        'views/account_move.xml',
    ],
    "license": "Other proprietary",
}
