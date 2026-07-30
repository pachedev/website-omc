# -*- coding: utf-8 -*-
import logging
import re
import json
import werkzeug.exceptions
import werkzeug.utils
import odoo
from odoo import http, tools
from odoo.http import request
from odoo.addons.web.controllers.home import SIGN_UP_REQUEST_PARAMS
from odoo.addons.web.controllers.utils import ensure_db

_logger = logging.getLogger(__name__)

MODULE = 'pdev_general_utilities'


def hex_to_rgb(hex_color):
    hex_color = (hex_color or '#000000').lstrip('#')
    if len(hex_color) != 6:
        return (0, 0, 0)
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _get_theme_values(param_obj):
    background = param_obj.get_param(f'{MODULE}.background')
    credential_opacity = param_obj.get_param(f'{MODULE}.credential_opacity') or '70'
    credential_border = param_obj.get_param(f'{MODULE}.credential_border')
    gradient_top_color = param_obj.get_param(f'{MODULE}.gradient_top_color') or '#000000'
    gradient_top_opacity = param_obj.get_param(f'{MODULE}.gradient_top_opacity') or '0'
    gradient_bottom_color = param_obj.get_param(f'{MODULE}.gradient_bottom_color') or '#000000'
    gradient_bottom_opacity = param_obj.get_param(f'{MODULE}.gradient_bottom_opacity') or '0'
    web_background_image_id = param_obj.get_param(f'{MODULE}.web_background_image_id')
    video_str = param_obj.get_param(f'{MODULE}.video') or ''

    disable_footer = param_obj.get_param(f'{MODULE}.web_remove_powered_by')
    disable_passkey = param_obj.get_param(f'{MODULE}.disable_passkey')

    top_rgb = hex_to_rgb(gradient_top_color)
    bottom_rgb = hex_to_rgb(gradient_bottom_color)

    video_id = ''
    match_url = re.search(r'(?:v=|\/embed\/|youtu\.be\/)([\w-]{11})', video_str)
    if match_url:
        video_id = match_url.group(1)

    background_src = ''
    background_color = param_obj.get_param(f'{MODULE}.color') or ''

    if background == 'image' and web_background_image_id:
        base_url = param_obj.get_param('web.base.url')
        background_src = (
            base_url
            + '/web/image?'
            + 'model=web.background.image&id='
            + web_background_image_id
            + '&field=image'
        )

    return {
        'background_src': background_src,
        'background_color': background_color,
        'credential_element_color': param_obj.get_param(f'{MODULE}.credential_element_color') or '#596773',
        'credential_opacity': float(credential_opacity) / 100,
        'credential_border': '#F8F9FA' if credential_border in ('with', False) else 'transparent',
        'gradient_top_color': gradient_top_color,
        'gradient_top_opacity': gradient_top_opacity,
        'gradient_bottom_color': gradient_bottom_color,
        'gradient_bottom_opacity': gradient_bottom_opacity,
        'gradient_top_r': top_rgb[0],
        'gradient_top_g': top_rgb[1],
        'gradient_top_b': top_rgb[2],
        'gradient_bottom_r': bottom_rgb[0],
        'gradient_bottom_g': bottom_rgb[1],
        'gradient_bottom_b': bottom_rgb[2],
        'video': video_id,
        'disable_footer': disable_footer not in ['False', '0', False, None],
        'disable_passkey': disable_passkey not in ['False', '0', False, None],
    }


class PdevHome(http.Controller):
    def _list_providers(self):
        try:
            providers = (
                request.env['auth.oauth.provider']
                .sudo()
                .search_read([('enabled', '=', True)])
            )
        except Exception:
            providers = []
        for provider in providers:
            return_url = request.httprequest.url_root + 'auth_oauth/signin'
            state = self._get_state(provider)
            params = dict(
                response_type='token',
                client_id=provider['client_id'],
                redirect_uri=return_url,
                scope=provider['scope'],
                state=json.dumps(state),
            )
            provider['auth_link'] = '%s?%s' % (
                provider['auth_endpoint'],
                werkzeug.urls.url_encode(params),
            )
        return providers

    def _get_state(self, provider):
        redirect = request.params.get('redirect') or 'web'
        if not redirect.startswith(('//', 'http://', 'https://')):
            redirect = '%s%s' % (
                request.httprequest.url_root,
                redirect[1:] if redirect[0] == '/' else redirect,
            )
        state = dict(
            d=request.session.db,
            p=provider['id'],
            r=werkzeug.urls.url_quote_plus(redirect),
        )
        token = request.params.get('token')
        if token:
            state['t'] = token
        return state

    def _login_redirect(self, uid, redirect=None):
        return redirect or '/web'

    @http.route('/web/login', type='http', auth='none')
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)
        if request.env.uid is None:
            if request.session.uid is None:
                request.env['ir.http']._auth_method_public()
            else:
                request.update_env(user=request.session.uid)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        is_oauth_installed = (
            request.env['ir.module.module']
            .sudo()
            .search([('state', '=', 'installed'), ('name', '=', 'auth_oauth')])
        )
        values['is_oauth_installed'] = is_oauth_installed
        values['providers'] = self._list_providers() if is_oauth_installed else []

        if request.httprequest.method == 'POST':
            try:
                credential = {
                    'login': request.params.get('login', '').strip(),
                    'password': request.params.get('password', ''),
                    'type': 'password',
                }
                try:
                    if request.env['res.users']._should_captcha_login(credential):
                        request.env['ir.http']._verify_request_recaptcha_token('login')
                except Exception:
                    pass
                auth_info = request.session.authenticate(request.env, credential)
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(auth_info['uid'], redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = 'Wrong login/password'
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = (
                    'Only employees can access this database. Please contact the administrator.'
                )

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')
        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        param_obj = request.env['ir.config_parameter'].sudo()
        login_style = param_obj.get_param(f'{MODULE}.login_style')
        values['signup_enabled'] = param_obj.get_param('auth_signup.invitation_scope') == 'b2c'
        values['reset_password_enabled'] = param_obj.get_param('auth_signup.reset_password')
        values.update(_get_theme_values(param_obj))

        if login_style in ('default', False, None):
            response = request.render('web.login', values)
        elif login_style == 'left':
            response = request.render(f'{MODULE}.left_login_template', values)
        elif login_style == 'right':
            response = request.render(f'{MODULE}.right_login_template', values)
        else:
            response = request.render(f'{MODULE}.middle_login_template', values)

        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
