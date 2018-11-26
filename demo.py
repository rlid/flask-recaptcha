from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap
from demo_forms import Recaptcha2Form, Recaptcha2InvisibleForm, Recaptcha3Form


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config["SECRET_KEY"] = "YOUR_SECRET_KEY"

# v2 test keys from https://developers.google.com/recaptcha/docs/faq
# to be replaced with your own
app.config["RECAPTCHA2_PUBLIC_KEY"] = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
app.config["RECAPTCHA2_PRIVATE_KEY"] = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

app.config["RECAPTCHA2_INVISIBLE_PUBLIC_KEY"] = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
app.config["RECAPTCHA2_INVISIBLE_PRIVATE_KEY"] = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

app.config["RECAPTCHA3_PUBLIC_KEY"] = "YOUR_RECAPTCHA3_PUBLIC_KEY"
app.config["RECAPTCHA3_PRIVATE_KEY"] = "YOUR_RECAPTCHA3_PRIVATE_KEY"

@app.route("/")
def index():
    return f'''
    <ul>
        <li><a href="{url_for("v2")}">ReCAPTCHA v2</a></li>
        <li><a href="{url_for("v2_invisible")}">ReCAPTCHA v2 Invisible</a></li>
        <li><a href="{url_for("v3")}">ReCAPTCHA v3</a></li>
    </ul>'''

@app.route("/v2", methods=["GET", "POST"])
def v2():
    form = Recaptcha2Form()
    if form.validate_on_submit():
        form.message.data = "[Success]" + form.message.data
    return render_template("demo.html", form=form)


@app.route("/v2-invisible", methods=["GET", "POST"])
def v2_invisible():
    form = Recaptcha2InvisibleForm()
    if form.validate_on_submit():
        form.message.data = "[Success]" + form.message.data
    return render_template("demo.html", form=form)


@app.route("/v3", methods=["GET", "POST"])
def v3():
    form = Recaptcha3Form()
    if form.validate_on_submit():
        form.message.data = "[Success]" + form.message.data
    return render_template("demo.html", form=form)


if __name__ == "__main__":
  app.run(debug=True)
 