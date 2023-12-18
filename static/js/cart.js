var updateBtns = document.getElementsByClassName('update-cart')

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var colorId = this.dataset.colorId
        var sizeId = this.dataset.sizeId
        var colorSizeId = this.dataset.color_size_id
        var action = this.dataset.action
        var quantityInput = document.getElementById('qty-' + productId);
        var quantity = quantityInput ? quantityInput.value : 1;

        if (action === 'delete_cart') {
            if (!(confirm("آیا مطمئن هستید که می خواهید سبد خرید را پاک کنید؟"))) {
                return;
            }
        }
        if (!(action === 'delete_item' || action === 'delete_cart')) {
            var intQtyInput = parseInt(quantity)
            if (intQtyInput > 0) {
                action = 'add';

            } else if (intQtyInput < 0) {
                action = 'remove';
            } else {
                action = '';
            }
        }

        updateUserOrder(productId, colorId, sizeId, colorSizeId, action, quantity)
    })
}

function updateCart() {
    var updateBtnsLazy = document.getElementsByClassName('update-cart-lazy')

    for (var i = 0; i < updateBtnsLazy.length; i++) {
        var button = updateBtnsLazy[i]
        var productId = button.dataset.product
        var colorSizeId = button.dataset.color_size_id
        var action = button.dataset.action
        var quantity = button.value;

        if (parseInt(quantity) < 0) {
            action = 'delete_item';
        }

        console.log('this is data: ', productId, colorSizeId, action, quantity,)
        updateUserOrder(productId, null, null, colorSizeId, action, quantity)


    }
}

function updateUserOrder(productId, colorId, sizeId, colorSizeId, action, quantity) {
    fetch(updateOrderUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'productId': productId,
            'colorId': colorId,
            'sizeId': sizeId,
            'colorSizeId': colorSizeId,
            'action': action,
            'quantity': quantity,
        })
    })


        .then((response) => {
            return response.json()
        })

        .then((data) => {
            location.reload()
        })

}