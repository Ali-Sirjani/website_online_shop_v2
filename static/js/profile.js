const notyf = new Notyf();

function displayErrorsForm(response, errorContainerId) {
    try {
        let form_errors = response.responseJSON.form.errors;
        var errorContainer = null;
        if (form_errors) {
            for (var key in form_errors) {
                errorContainer = document.getElementById(errorContainerId);
                errorContainer.innerHTML = form_errors[key];
                errorContainer.style.display = 'block';
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
        errorContainer = document.getElementById(errorContainerId);
        errorContainer.textContent = 'تعداد درخواست‌ها زیاد است. لطفاً دقایقی دیگر مجدداً تلاش کنید.';
        errorContainer.style.display = 'block';
    }
}

function removeIsInvalidElements(formElements) {
    for (var i = 0; i < formElements.length; i++) {
        let element = formElements[i];
        element.classList.remove('is-invalid');
        let feedbackAreaa = document.querySelector(`#invalid-feedback-${element.name}`);
        if (feedbackAreaa) {
            feedbackAreaa.style.display = "none";
        }
    }
}

function setUsernameAjax() {
    let myForm = document.getElementById('set_username_form');
    let formElements = myForm.elements;

    removeIsInvalidElements(formElements);
    let setUsernameBtn = document.getElementById('setUsernameBtn');
    setUsernameBtn.innerHTML = `در حال تغییر....`;

    var data = new FormData(myForm);

    $.ajax({
        type: 'POST',
        url: setUsernameUrl,
        data: data,
        cache: false,
        processData: false,
        contentType: false,

        success: function (response) {
            setUsernameBtn.innerHTML = `تغییر نام کاربری`;
            location.reload();
            window.scrollTo(0, 0);
        },
        error: function (response) {
            displayErrorsForm(response, "set_username_error_container");
            setUsernameBtn.innerHTML = `تغییر نام کاربری`;
        }
    });
}

function updateProfileAjax() {
    let myForm = document.getElementById('profile_form');
    let formElements = myForm.elements;

    removeIsInvalidElements(formElements);
    let updateProfileBtn = document.getElementById('updateProfileBtn');
    updateProfileBtn.innerHTML = `در حال تغییر....`;

    var data = new FormData(myForm);

    $.ajax({
        type: 'POST',
        url: profileUrd,
        headers: {
            'X-CSRFToken': csrftoken,
        },
        data: data,
        processData: false,
        contentType: false,

        success: function (response) {
            updateProfileBtn.innerHTML = `ذخیره تغییرات`;
            location.reload();
            window.scrollTo(0, 0);
        },
        error: function (response) {
            displayErrorsForm(response, "set_username_error_container");
            updateProfileBtn.innerHTML = `ذخیره تغییرات`;
        }
    });

}

function addressAjax() {
    let myForm = document.getElementById('address_form_id');
    let formElements = myForm.elements;

    removeIsInvalidElements(formElements);

    let changePasswordBtn = document.getElementById('addressBtn');
    changePasswordBtn.innerHTML = `در حال ارسال....`;
    var operationType = changePasswordBtn.dataset.operation;

    var requestUrl = null
    if (operationType === "create") {
        requestUrl = addressCreateUrl;
    }
    if (operationType === "update") {
        requestUrl = addressUpdateUrl;
    }

    var data = new FormData(myForm);

    $.ajax({
        type: 'POST',
        url: requestUrl,
        data: data,
        cache: false,
        processData: false,
        contentType: false,

        success: function (response) {
            changePasswordBtn.innerHTML = `ارسال`;
            location.reload();
            window.scrollTo(0, 0);
        },
        error: function (response) {
            displayErrorsForm(response, "address_error_container");
            changePasswordBtn.innerHTML = `ارسال`;
        }
    });
}

function changePassword() {
    let myForm = document.getElementById('change_password_form');
    let formElements = myForm.elements;

    removeIsInvalidElements(formElements);

    let changePasswordBtn = document.getElementById('changePasswordBtn');
    changePasswordBtn.innerHTML = `در حال تغییر رمز عبور....`;

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
            location.reload();
            window.scrollTo(0, 0);
        },
        error: function (response) {
            displayErrorsForm(response, "change_pass_error_container");
            changePasswordBtn.innerHTML = `تغییر رمز عبور`;
        }
    });
}

function setPassword() {
    let myForm = document.getElementById('set_password_form');
    let formElements = myForm.elements;

    removeIsInvalidElements(formElements);

    let changePasswordBtn = document.getElementById('changePasswordBtn');
    changePasswordBtn.innerHTML = `در حال قراردادن رمز عبور....`;


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
            location.reload();
            window.scrollTo(0, 0);
        },
        error: function (response) {
            displayErrorsForm(response, "set_pass_error_container");
            changePasswordBtn.innerHTML = `قراردادن رمز عبور`;
        }
    });
}

function showCreateOrUpdateFormAddress(event) {
    var operationType = event.target.dataset.operationForm
    var addressForm = document.getElementById('address_form_id')
    var addressBtnForm = addressForm.querySelector('#addressBtn')
    var addressFormTitle = addressForm.querySelector('#address_form_title')

    var formElements = addressForm.elements;
    var errorContainer = document.getElementById('address_error_container');
    errorContainer.style.display = 'none';

    for (var i = 0; i < formElements.length; i++) {
        let element = formElements[i];
        element.classList.remove('is-invalid', 'is-valid');
        let feedbackAreaa = document.querySelector(`#invalid-feedback-${element.name}`);
        if (feedbackAreaa) {
            feedbackAreaa.style.display = "none";
        }
    }

    if (operationType === 'create') {
        addressForm.reset();
        addressBtnForm.dataset.operation = 'create';
        addressForm.style.display = 'block';
        addressFormTitle.innerHTML = 'ساخت آدرس جدید';
    }

    if (operationType === 'update') {
        addressForm.reset();
        addressForm.state.value = event.target.dataset.state;
        addressForm.city.value = event.target.dataset.city;
        addressForm.address.value = event.target.dataset.address;
        addressForm.plate.value = event.target.dataset.plate;
        addressForm.pk.value = event.target.dataset.addressId;
        addressBtnForm.dataset.operation = 'update';
        addressForm.style.display = 'block';
        addressFormTitle.innerHTML = 'ویرایش آدرس counter'.replace('counter', event.target.dataset.counter);
    }

    event.preventDefault();
}

function deleteAddress(event) {
    var messageConfirm = 'پاک کردن آدرس شماره counter'.replace('counter', event.target.dataset.counter)
    if (confirm(messageConfirm)) {
        var pkAddress = event.target.dataset.pk

        fetch(addressDeleteUrl, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({'pk': pkAddress}),
            }
        )
            .then(response => {
                if (!response.ok) {
                    throw new Error(`${response.status}`);
                }
                return response.json();
            })

            .then(data => {
                console.log(data);
                location.reload();
            })

            .catch((error) => {
                console.log('this is type: ', typeof(error))
                if (error.message === '404'){
                    alert("اطاعات ارسالی غلط هستند! لطفا از دوباره امتحان کنید.");
                    location.reload();
                }
            });

    }
    event.preventDefault();
}
