# -*- coding: utf-8 -*-
import logging
import werkzeug
from werkzeug.urls import url_encode
from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.home import Home
from odoo.exceptions import UserError
from odoo.http import request
from .main_login import _get_theme_values

_logger = logging.getLogger(__name__)

MODULE = 'pdev_general_utilities'


class AuthSignupHome(Home):
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        values = self.get_auth_signup_qcontext()

        if not values.get('token') and not values.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in values and request.httprequest.method == 'POST':
            try:
                self.do_signup(values)
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(values.get('login')),
                    order=User._get_login_order(),
                    limit=1,
                )
                template = request.env.ref(
                    'auth_signup.mail_template_user_signup_account_created',
                    raise_if_not_found=False,
                )
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                values['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                User = request.env['res.users']
                if (
                    User.sudo()
                    .with_context(active_test=False)
                    .search_count(User._get_login_domain(values.get('login')), limit=1)
                ):
                    values['error'] = _('Another user is already registered using this email address.')
                else:
                    _logger.warning('%s', e)
                    values['error'] = _('Could not create a new account.') + '\n' + str(e)

        elif 'signup_email' in values:
            user = (
                request.env['res.users']
                .sudo()
                .search(
                    [('email', '=', values.get('signup_email')), ('state', '!=', 'new')],
                    limit=1,
                )
            )
            if user:
                return request.redirect(
                    '/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'})
                )

        conf_param = request.env['ir.config_parameter'].sudo()
        login_style = conf_param.get_param(f'{MODULE}.login_style')

        is_oauth_installed = (
            request.env['ir.module.module']
            .sudo()
            .search([('state', '=', 'installed'), ('name', '=', 'auth_oauth')])
        )
        values['is_oauth_installed'] = is_oauth_installed
        values['providers'] = self._list_providers() if is_oauth_installed else []
        values['signup_enabled'] = conf_param.get_param('auth_signup.invitation_scope') == 'b2c'
        values['reset_password_enabled'] = conf_param.get_param('auth_signup.reset_password')
        values.update(_get_theme_values(conf_param))

        if login_style in ('default', False, None):
            response = request.render('auth_signup.signup', values)
        elif login_style == 'left':
            response = request.render(f'{MODULE}.left_signup_template', values)
        elif login_style == 'right':
            response = request.render(f'{MODULE}.right_signup_template', values)
        else:
            response = request.render(f'{MODULE}.middle_signup_template', values)

        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
