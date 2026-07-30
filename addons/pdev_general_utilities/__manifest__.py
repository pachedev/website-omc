# -*- coding: utf-8 -*-
{
    "name": "Pachedev - General Utilities",
    "category": "Extra Tools",
    "version": "19.0.1.0.0",
    "author": "Pachedev",
    "maintainer": "Pachedev",
    "company": "Pachedev",
    "website": "https://pachedev.com",
    "depends": ["base", "base_setup", "web", "auth_signup"],
    "summary": """
		Allows to customize odoo authentication pages and hide menus to specific users.
	""",
    "description": """
		Allows to customize the login, signup and reset password pages with a configurable orientation and backgroup as well as to place an icon to see the password and hide menus to specific users.
	""",
    "data": [
        # Security
        "security/security.xml",
        "security/ir.model.access.csv",
        # Views
        "views/res_config_settings_views.xml",
        "views/login/left_login_template.xml",
        "views/login/middle_login_template.xml",
        "views/login/right_login_template.xml",
        "views/signup/left_signup_template.xml",
        "views/signup/middle_signup_template.xml",
        "views/signup/right_signup_template.xml",
        "views/reset_password/left_reset_password_template.xml",
        "views/reset_password/middle_reset_password_template.xml",
        "views/reset_password/right_reset_password_template.xml",
        "views/res_users_views.xml",
        "views/web_background_image_views.xml",
        # Menus
        "menus/menus.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "pdev_general_utilities/static/src/css/web_styles.css",
        ],
        "web.assets_backend": [
            "pdev_general_utilities/static/src/js/dialog/**/*",
            "pdev_general_utilities/static/src/css/general_styles.css",
            "pdev_general_utilities/static/src/scss/navbar.scss",
            "pdev_general_utilities/static/src/scss/custom_colors.scss",
            "pdev_general_utilities/static/src/search/control_panel/control_panel.xml",
            "pdev_general_utilities/static/src/views/form/form_status_indicator/form_status_indicator.xml",
            "pdev_general_utilities/static/src/views/form/form_status_indicator/form_status_indicator.js",
            "pdev_general_utilities/static/src/views/form/form_controller/form_controller.xml",
        ],
    },
    "images": [],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
    "post_init_hook": "load_default_background_image",
    "uninstall_hook": "remove_system_parameters",
}
