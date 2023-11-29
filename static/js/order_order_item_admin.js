function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

jQuery(function ($) {
    $(document).ready(function () {
        $("#id_product").change(function () {
            $.ajax({
                url: "http://127.0.0.1:8000/products/admin-drop/color-size/",
                type: "POST",
                data: JSON.stringify({productId: $(this).val()}),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function (result) {
                    console.log(result);
                    var cols = $("#id_color_size");
                    cols.empty();

                    if (result) {
                        for (var key in result) {
                            cols.append(new Option(key, result[key]));
                        }
                    } else {
                        cols.append(new Option());
                    }
                },
                error: function (e) {
                    console.error(JSON.stringify(e));
                },
            });
        });
    });
});
