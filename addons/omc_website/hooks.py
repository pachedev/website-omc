# -*- coding: utf-8 -*-

# Download stays out of the main menu: the header CTA already covers it. FAQ is
# abbreviated in both languages so the menu still fits on one line.
MENU_ITEMS = [
    # (en_US, es_MX, url, sequence)
    ('Home', 'Inicio', '/', 10),
    ('How it works', 'Cómo funciona', '/how-it-works', 20),
    ('Use cases', 'Casos de uso', '/use-cases', 30),
    ('Pricing', 'Precios', '/pricing', 40),
    ('FAQ', 'FAQ', '/faq', 50),
    ('Contact us', 'Contáctanos', '/contactus', 60),
]


HEADER_CTA_ARCH = """<data>
    <xpath expr="//div[@data-name='Button']//a" position="replace">
        <div class="d-flex align-items-center justify-content-end gap-3">
            <t t-if="len(frontend_languages) &gt; 1" t-call="portal.language_selector">
                <t t-set="codes" t-value="True"/>
                <t t-set="no_text" t-value="True"/>
                <t t-set="_div_classes" t-value="'omc-header-lang d-flex align-items-center'"/>
                <t t-set="_btn_class" t-value="'btn btn-sm'"/>
            </t>
            <a href="/download" class="btn btn-primary omc-header-cta">Download the app</a>
        </div>
    </xpath>
    <xpath expr="//div[hasclass('header-center')][1]" position="attributes">
        <attribute name="class">col-md-6 d-none d-md-block header-center</attribute>
    </xpath>
    <xpath expr="//div[hasclass('header-center')][2]" position="attributes">
        <attribute name="class">col-md-3 d-none d-md-block header-center</attribute>
    </xpath>
    <xpath expr="//t[@t-call='theme_nextbiz.bizople_mobile_bottom_icon_bar']" position="replace"/>
</data>"""


def _setup_sidebar_logo(env):
    """Fill theme_nextbiz's `sidebar_logo`, used by the mobile sidebar header.

    It is a separate Binary field on `website` that ships empty, so the mobile
    menu renders a broken image until it is set. The site logo works as-is
    there: the sidebar has a white background.
    """
    for website in env['website'].search([]):
        if 'sidebar_logo' in website._fields and not website.sidebar_logo:
            website.sidebar_logo = website.logo


def _setup_theme_header(env):
    """Enable nextbiz header 8 and swap its "Get Quote" CTA for ours.

    Theme views are theme.ir.ui.view templates; their real per-website
    ir.ui.view copies carry the theme key but no xmlid, so they can only be
    reached through the ORM.
    """
    View = env['ir.ui.view'].with_context(active_test=False)
    headers = View.search([('key', '=', 'theme_nextbiz.theme_nextbiz_header8')])
    headers.write({'active': True})
    for header in headers:
        if View.search_count([('key', '=', 'omc_website.header_cta'),
                              ('inherit_id', '=', header.id)]):
            continue
        cta = env['ir.ui.view'].create({
            'name': 'OMC Header CTA',
            'type': 'qweb',
            'mode': 'extension',
            'inherit_id': header.id,
            'key': 'omc_website.header_cta',
            'website_id': header.website_id.id,
            'arch': HEADER_CTA_ARCH,
        })
        cta.update_field_translations('arch_db', {
            'es_MX': {'Download the app': 'Descarga la app'},
        })


def _apply_brand_palette(env):
    """Activate the 'omc-1' palette through the editor's own mechanism.

    Same approach as the Website customize panel: the choice is persisted as an
    SCSS customization, so it survives theme updates instead of relying on a
    map-merge that has to outrank the theme.
    """
    env['website.assets'].make_scss_customization(
        '/website/static/src/scss/options/user_values.scss',
        {'color-palettes-name': "'omc-1'"},
    )


def post_init_hook(env):
    """Configure palette, languages, website defaults, homepage and main menu."""
    _apply_brand_palette(env)
    lang_model = env['res.lang']
    lang_model._activate_lang('en_US')
    en = lang_model.search([('code', '=', 'en_US')], limit=1)
    es = lang_model.search([('code', '=', 'es_MX')], limit=1)

    _setup_theme_header(env)
    _setup_sidebar_logo(env)

    # Our pages own these URLs; drop the default/theme pages that shipped on
    # them (duplicate URLs would also break canonical/hreflang resolution).
    for url, xmlid in [
        ('/', 'omc_website.page_home'),
        ('/contactus-thank-you', 'omc_website.page_contact_thanks'),
    ]:
        page = env.ref(xmlid)
        env['website.page'].search([
            ('url', '=', url), ('id', '!=', page.id),
        ]).unlink()

    # This site has no blog: website_blog only comes in as a theme dependency,
    # so its menu entries go away and the seed blog is archived (which also
    # keeps /blog out of the sitemap).
    env['website.menu'].search([('url', 'like', '/blog')]).unlink()
    blogs = env['blog.blog'].with_context(active_test=False).search([])
    if blogs:
        blogs.write({'active': False})

    # Theme demo pages we do not use: unpublish so they stop being reachable
    # and drop out of the sitemap.
    env['website.page'].search([
        ('url', 'in', ['/coming-soon', '/help-center', '/thank-you']),
    ]).write({'is_published': False, 'website_indexed': False})

    # /go/odoo is a redirect, not content: keep crawlers off it.
    site = env['website'].search([], limit=1)
    robots = site.robots_txt or ''
    for rule in ('Disallow: /blog', 'Disallow: /go'):
        if rule not in robots:
            robots = (robots.rstrip() + '\n' + rule).strip()
    site.robots_txt = robots

    # The sitemap is cached in attachments; drop it so the next request rebuilds
    # it from the pages that are actually published.
    env['ir.attachment'].sudo().search([('name', 'like', 'sitemap')]).unlink()

    # Brand mailbox: contact form (email_to) and any outgoing mail identity.
    env['res.company'].search([]).filtered(lambda c: not c.email).write({
        'email': 'contact@pachedev.com',
    })

    for website in env['website'].search([]):
        vals = {
            'name': 'Odoo Mobile Client',
            'homepage_url': False,
            'domain': 'https://omc.pachedev.com',
        }
        if en:
            vals['default_lang_id'] = en.id
            lang_ids = en.ids + (es.ids if es else [])
            vals['language_ids'] = [(6, 0, lang_ids)]
        website.write(vals)

        top_menu = website.menu_id
        if not top_menu:
            continue
        top_menu.child_id.unlink()
        for name_en, name_es, url, sequence in MENU_ITEMS:
            menu = env['website.menu'].with_context(lang='en_US').create({
                'name': name_en,
                'url': url,
                'sequence': sequence,
                'parent_id': top_menu.id,
                'website_id': website.id,
            })
            if es:
                menu.with_context(lang='es_MX').name = name_es
