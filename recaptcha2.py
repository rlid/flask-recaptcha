import logging

import requests
from flask import Markup, current_app, json, request
from werkzeug.urls import url_encode
from wtforms import ValidationError
from wtforms.fields import Field

logger = logging.getLogger(__name__)

JSONEncoder = json.JSONEncoder

RECAPTCHA_SRC = 'https://www.google.com/recaptcha/api.js'
RECAPTCHA_SCRIPT = '<script src="{src}" async defer></script>'
RECAPTCHA_INVISIBLE_SCRIPT = '''
<script>
  function onSubmit(token) {{
    document.getElementById("{form_id}").submit();
  }}
</script>
'''

RECAPTCHA_TEMPLATE = '''
{script}
<{tag_name} class="g-recaptcha {class_}" {data_attributes}>{label}</{tag_name}>
'''

RECAPTCHA_VERIFY_SERVER = 'https://www.google.com/recaptcha/api/siteverify'
RECAPTCHA_ERROR_CODES = {
    'missing-input-secret': 'The secret parameter is missing.',
    'invalid-input-secret': 'The secret parameter is invalid or malformed.',
    'missing-input-response': 'The response parameter is missing.',
    'invalid-input-response': 'The response parameter is invalid or malformed.'
}


class RecaptchaValidator(object):
    """Validates a ReCaptcha."""

    def __init__(self, message=None):
        if message is None:
            message = "Please verify that you are not a robot."
        self.message = message

    def __call__(self, form, field):
        if current_app.testing:
            return True

        if request.json:
            response = request.json.get('g-recaptcha-response', '')
        else:
            response = request.form.get('g-recaptcha-response', '')

        remote_ip = request.remote_addr

        if not response:
            logger.warning("Token is not ready or incorrect configuration (check JavaScript error log).")
            raise ValidationError(field.gettext(self.message))

        if not RecaptchaValidator._validate_recaptcha(field, response, remote_ip):
            field.recaptcha_error = 'incorrect-captcha-sol'
            raise ValidationError(field.gettext(self.message))

    @staticmethod
    def _validate_recaptcha(field, response, remote_addr):
        """Performs the actual validation."""
        private_key_name = 'RECAPTCHA2_INVISIBLE_PRIVATE_KEY' if field.invisible_on_load else 'RECAPTCHA2_PRIVATE_KEY'
        try:
            private_key = current_app.config[private_key_name]
        except KeyError:
            raise RuntimeError(f"{private_key_name} is not set in app config.")

        data = {
            'secret': private_key,
            'remoteip': remote_addr,
            'response': response
        }

        http_response = requests.post(RECAPTCHA_VERIFY_SERVER, data)

        if http_response.status_code != 200:
            return False

        json_resp = http_response.json()

        if json_resp["success"]:
            logger.info(json_resp)
            return True
        else:
            logger.warning(json_resp)

        for error in json_resp.get("error-codes", []):
            if error in RECAPTCHA_ERROR_CODES:
                raise ValidationError(RECAPTCHA_ERROR_CODES[error])

        return False


class RecaptchaWidget(object):
    def __call__(self, field, class_="", form_id=None, **kwargs):
        """Returns the recaptcha input HTML."""
        public_key_name = 'RECAPTCHA2_INVISIBLE_PUBLIC_KEY' if field.invisible_on_load else 'RECAPTCHA2_PUBLIC_KEY'
        try:
            public_key = current_app.config[public_key_name]
        except KeyError:
            raise RuntimeError(f"{public_key_name} is not set in app config.")

        if field.invisible_on_load and not form_id:
            raise RuntimeError("form_id must be specified if invisible_on_load is set to True for reCAPTCHA field.")

        html = current_app.config.get('RECAPTCHA2_HTML')
        if html:
            return Markup(html)
        params = current_app.config.get('RECAPTCHA2_PARAMETERS')
        source = RECAPTCHA_SRC
        if params:
            source += '?' + url_encode(params)

        script = RECAPTCHA_SCRIPT.format(src=source)
        if field.invisible_on_load:
            script += RECAPTCHA_INVISIBLE_SCRIPT.format(form_id=form_id)

        attrs = current_app.config.get('RECAPTCHA2_DATA_ATTRS', {})
        attrs['sitekey'] = public_key
        if field.invisible_on_load:
            attrs['callback'] = 'onSubmit'
        snippet = ' '.join(['data-%s="%s"' % (k, attrs[k]) for k in attrs])

        return Markup(RECAPTCHA_TEMPLATE.format(script=script,
                                                tag_name="button" if field.invisible_on_load else "div",
                                                class_=class_,
                                                data_attributes=snippet,
                                                label=field.label.text))


class RecaptchaField(Field):
    widget = RecaptchaWidget()

    # error message if recaptcha validation fails
    recaptcha_error = None

    def __init__(self, label='', validators=None, invisible_on_load=False, **kwargs):
        self.invisible_on_load = invisible_on_load
        validators = validators or [RecaptchaValidator()]
        super(RecaptchaField, self).__init__(label, validators, **kwargs)
