const notyf = new Notyf();

function changePassword() {
    // Similar structure to the Login function
    // old password
    let oldPassword_id = document.getElementById(`id_oldpassword`);
    let oldPasswordFeedbackArea = document.querySelector(`#invalid-feedback-oldpassword`);
    // password1
    let password1Id = document.getElementById(`id_password1`);
    let password1IdFeedbackArea = document.querySelector(`#invalid-feedback-password1`);
    // password2
    let password2Id = document.getElementById(`id_password2`);
    let password2IdFeedbackArea = document.querySelector(`#invalid-feedback-password2`);

    // Repeat for other fields in the form
    // old password
    oldPassword_id.classList.remove('is-invalid');
    oldPasswordFeedbackArea.style.display = "none";
    // password1
    password1Id.classList.remove('is-invalid');
    password1IdFeedbackArea.style.display = "none";
    // password2
    password2Id.classList.remove('is-invalid');
    password2IdFeedbackArea.style.display = "none";
    // Repeat for other fields

    let changePasswordBtn = document.getElementById('changePasswordBtn');
    changePasswordBtn.innerHTML = `در حال تغییر رمز عبور....`;
    let myForm = document.getElementById('change_password_form');

    var data = new FormData(myForm);
    $.ajax({
        type: 'POST',
        url: changePasswordUrl,
        data: data,
        cache: false,
        processData: false,
        contentType: false,

        success: function (response) {
            changePasswordBtn.innerHTML = `تغییر رمز عبور`;
            console.log('success');
            location.reload();
            window.scrollTo(0, 0);
        },
        error: function (response) {
            try {
                let form_errors = response.responseJSON.form.errors;
                if (form_errors) {
                    for (var key in form_errors) {
                        notyf.error({
                            message: form_errors[key],
                            duration: 0,
                            dismissible: true
                        })
                    }
                }

                let fields_name = response.responseJSON.form.fields;
                for (var key in fields_name) {
                    let field_id = document.getElementById(`id_${key}`)
                    let feedbackAreaa = document.querySelector(`#invalid-feedback-${key}`);
                    if (fields_name[key].errors.length > 0) {
                        for (var fieldkey in fields_name[key].errors) {
                            field_id.classList.add('is-invalid');
                            feedbackAreaa.style.display = "block";
                            feedbackAreaa.innerHTML = `${fields_name[key].errors[fieldkey]}`
                        }
                    } else {
                        field_id.classList.remove('is-invalid');
                        feedbackAreaa.style.display = "none";
                        field_id.classList.add('is-valid');
                    }
                }
            } catch (TypeError) {
                var errorContainer = document.getElementById('change_pass_error_container');
                errorContainer.textContent = 'تعداد درخواست‌ها زیاد است. لطفاً دقایقی دیگر مجدداً تلاش کنید.';
                errorContainer.style.display = 'block';
            }
            changePasswordBtn.innerHTML = `تغییر رمز عبور`;
        }
    });
}

function setPassword() {
    // password1
    let password1Id = document.getElementById(`id_password1`);
    let password1IdFeedbackArea = document.querySelector(`#invalid-feedback-password1`);
    // password2
    let password2Id = document.getElementById(`id_password2`);
    let password2IdFeedbackArea = document.querySelector(`#invalid-feedback-password2`);

    // password1
    password1Id.classList.remove('is-invalid');
    password1IdFeedbackArea.style.display = "none";
    // password2
    password2Id.classList.remove('is-invalid');
    password2IdFeedbackArea.style.display = "none";


    let changePasswordBtn = document.getElementById('changePasswordBtn');
    changePasswordBtn.innerHTML = `در حال قراردادن رمز عبور....`;
    let myForm = document.getElementById('set_password_form');

    var data = new FormData(myForm);
    $.ajax({
        type: 'POST',
        url: setPasswordUrl,
        data: data,
        cache: false,
        processData: false,
        contentType: false,

        success: function (response) {
            changePasswordBtn.innerHTML = `قراردادن رمز عبور`;
            console.log('success');
            location.reload();
            window.scrollTo(0, 0);
        },
        error: function (response) {
            try {
                let form_errors = response.responseJSON.form.errors;
                if (form_errors) {
                    for (var key in form_errors) {
                        notyf.error({
                            message: form_errors[key],
                            duration: 0,
                            dismissible: true
                        })
                    }
                }

                let fields_name = response.responseJSON.form.fields;
                for (var key in fields_name) {
                    let field_id = document.getElementById(`id_${key}`)
                    let feedbackAreaa = document.querySelector(`#invalid-feedback-${key}`);
                    if (fields_name[key].errors.length > 0) {
                        for (var fieldkey in fields_name[key].errors) {
                            field_id.classList.add('is-invalid');
                            feedbackAreaa.style.display = "block";
                            feedbackAreaa.innerHTML = `${fields_name[key].errors[fieldkey]}`
                        }
                    } else {
                        field_id.classList.remove('is-invalid');
                        feedbackAreaa.style.display = "none";
                        field_id.classList.add('is-valid');
                    }
                }
            } catch (TypeError) {
                var errorContainer = document.getElementById('set_pass_error_container');
                errorContainer.textContent = 'تعداد درخواست‌ها زیاد است. لطفاً دقایقی دیگر مجدداً تلاش کنید.';
                errorContainer.style.display = 'block';
            }
            changePasswordBtn.innerHTML = `قراردادن رمز عبور`;
        }
    });
}