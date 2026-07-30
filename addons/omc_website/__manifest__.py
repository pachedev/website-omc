# -*- coding: utf-8 -*-
{
    'name': 'Odoo Mobile Client — Website',
    'version': '19.0.2.0.0',
    'category': 'Website',
    'summary': 'Marketing website and contact leads for Odoo Mobile Client (OMC)',
    'description': """
Marketing site for Odoo Mobile Client (OMC):
home, how it works, free vs advanced, use cases, pricing,
download, FAQ, contact, privacy policy and terms & conditions.

Brand identity: 'omc-1' palette with color combinations, design tokens
and own snippet styles on top of theme_nextbiz.

Contact: own form (/contactus) with honeypot, Cloudflare Turnstile,
privacy consent and an internal lead pipeline with manual conversion
to CRM (when crm is installed).

English source copy, Spanish (es_MX) translations via i18n.
""",
    'author': 'Pachedev',
    'website': 'https://omc.pachedev.com',
    'license': 'Other proprietary',
    'depends': [
        'website',
        'theme_nextbiz',
        'mail',
        'website_cf_turnstile',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Data (noupdate seeds)
        'data/demo_credentials.xml',
        # Backend views
        'views/omc_contact_lead_views.xml',
        'views/omc_affiliate_views.xml',
        # Layout
        'views/layout.xml',
        'views/affiliate_cta.xml',
        'views/header_footer.xml',
        # Pages
        'views/page_home.xml',
        'views/page_how_it_works.xml',
        'views/page_free_vs_advanced.xml',
        'views/page_use_cases.xml',
        'views/page_pricing.xml',
        'views/page_download.xml',
        'views/page_faq.xml',
        'views/page_contact.xml',
        'views/page_privacy.xml',
        'views/page_terms.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'omc_website/static/src/scss/primary_variables.scss',
        ],
        'web.assets_frontend': [
            'omc_website/static/src/scss/tokens.scss',
            'omc_website/static/src/scss/omc_frontend.scss',
            'omc_website/static/src/js/demo_credentials.js',
        ],
        # Loaded eagerly: in the lazy bundle the scroll listener would only
        # attach after the page had already been painted and scrolled.
        'web.assets_frontend_minimal': [
            'omc_website/static/src/js/header_scroll.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}
