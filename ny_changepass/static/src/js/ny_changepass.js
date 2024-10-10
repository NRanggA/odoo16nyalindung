odoo.define('ny_changepass.password_visibility', function (require) {
    "use strict";

    $(document).ready(function () {
        var passwordField = $("input[name='confirm_password']");
        var toggleButton = $("#toggle-password-visibility");

        console.log(passwordField);
        console.log(toggleButton);

        if (passwordField.length && toggleButton.length) {
            toggleButton.on("click", function () {
                if (passwordField.attr("type") === "password") {
                    passwordField.attr("type", "text");
                    toggleButton.html('<span class="fa fa-eye-slash" title="Hide Password"></span>');
                } else {
                    passwordField.attr("type", "password");
                    toggleButton.html('<span class="fa fa-eye" title="Show Password"></span>');
                }
            });
        }
    });
});
