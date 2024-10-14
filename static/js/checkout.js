const notyfCheckout = new Notyf();

function showErrorsFrom(form) {
    let form_errors = form.errors;

    if (form_errors) {
        for (var key in form_errors) {
            var noneFieldErrors = document.getElementById('noneFieldErrors');
            noneFieldErrors.innerHTML = form_errors[key];
            noneFieldErrors.style.display = 'block';
        }
    }

    let fields_name = form.fields;
    for (var key in fields_name) {
        if (key !== 'total') {
            let field_element = document.getElementById(`id_${key}`)
            console.log('this is : ', form.fields[key]['value']);
            let value_field = form.fields[key]['value'];
            if (value_field) {
                console.log('this is value: ', `id_${key}`)
                field_element.value = value_field;
            }

            let feedbackAreaa = document.querySelector(`#invalid-feedback-${key}`);
            if (fields_name[key].errors.length > 0) {
                for (var fieldkey in fields_name[key].errors) {
                    feedbackAreaa.style.display = "block";
                    feedbackAreaa.style.marginBottom = '20px';
                    feedbackAreaa.style.fontSize = '15px';
                    feedbackAreaa.innerHTML = `${fields_name[key].errors[fieldkey]}`
                }
            } else {
                feedbackAreaa.style.display = "none";
            }
        }
    }

}

var setAddressBtn = document.getElementsByClassName('set-address');
var setAddressBtnLength = setAddressBtn.length;

for (var i = 0; i < setAddressBtnLength; i++) {
    setAddressBtn[i].addEventListener('click', function () {
        document.querySelector('input[name="state"]').value = this.dataset.state;
        document.querySelector('input[name="city"]').value = this.dataset.city;
        document.querySelector('textarea[name="address"]').value = this.dataset.address;
        document.querySelector('input[name="plate"]').value = this.dataset.plate;
        // Get the collapse element associated with the button
        var collapseId = $(this).closest('.ltn__checkout-single-content').find('.collapse').attr('id');

        // Close the collapse
        $('#' + collapseId).collapse('hide');

        var offset = $('#payment_form').offset().top - 245;
        $('html, body').animate({
            scrollTop: offset
        }, 100);
    });
}

function setProfileInfo(event) {
    event.preventDefault();
    $.ajax({
        type: 'GET',
        url: setProfileInfoUrl,
        cache: false,
        processData: false,
        contentType: false,

        success: function (response) {
            document.querySelector('input[name="first_name"]').value = response.first_name;
            document.querySelector('input[name="last_name"]').value = response.last_name;
            document.querySelector('input[name="email"]').value = response.email;
            document.querySelector('input[name="phone"]').value = response.phone;

        },

        error: function (response) {
            event.preventDefault();
        }

    })
}

