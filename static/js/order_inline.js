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
        $("[id^='id_items-'][id$='-product']").change(function () {
            console.log('Before result');
            var index = this.id.match(/\d+/)[0]; // Extract the index from the element's id
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
                    var cols = $("#id_items-" + index + "-color_size");
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
