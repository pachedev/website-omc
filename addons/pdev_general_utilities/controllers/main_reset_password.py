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


class AuthResetPasswordHome(Home):
    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        values = self.get_auth_signup_qcontext()

        if not values.get('token') and not values.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in values and request.httprequest.method == 'POST':
            try:
                if values.get('token'):
                    self.do_signup(values)
                    values['message'] = _('Your password has been reset successfully.')
                else:
                    login = values.get('login')
                    assert login, _('No login provided.')
                    _logger.info(
                        'Password reset attempt for <%s> by user <%s> from %s',
                        login,
                        request.env.user.login,
                        request.httprequest.remote_addr,
                    )
                    request.env['res.users'].sudo().reset_password(login)
                    values['message'] = _('Password reset instructions sent to your email')
            except UserError as e:
                values['error'] = e.args[0]
            except SignupError:
                values['error'] = _('Could not reset your password')
                _logger.exception('error when resetting password')
            except Exception as e:
                values['error'] = str(e)

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
            response = request.render('auth_signup.reset_password', values)
        elif login_style == 'left':
            response = request.render(f'{MODULE}.left_reset_password_template', values)
        elif login_style == 'right':
            response = request.render(f'{MODULE}.right_reset_password_template', values)
        else:
            response = request.render(f'{MODULE}.middle_reset_password_template', values)

        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
