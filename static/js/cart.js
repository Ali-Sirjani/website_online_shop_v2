var updateBtns = document.getElementsByClassName('update-cart');
var updateBtnsLength = updateBtns.length;

for (var i = 0; i < updateBtnsLength; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product;
        var colorId = this.dataset.colorId;
        var sizeId = this.dataset.sizeId;
        var colorSizeId = this.dataset.color_size_id;
        var action = this.dataset.action;
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

        updateUserOrder(productId, colorId, sizeId, colorSizeId, action, quantity, true);
    })
}

function updateCartAuthenticatedUser() {
    var updateBtnsLazy = document.getElementsByClassName('update-cart-lazy');
    var updateBtnsLazyLength = updateBtnsLazy.length;

    for (var i = 0; i < updateBtnsLazyLength; i++) {
        var button = updateBtnsLazy[i];
        var productId = button.dataset.product;
        var colorSizeId = button.dataset.color_size_id;
        var action = button.dataset.action;
        var quantity = button.value;

        if (parseInt(quantity) < 0) {
            action = "delete_item";
        }

        updateUserOrder(productId, null, null, colorSizeId, action, quantity, true);

    }
}

function updateCartAnonymousUser() {
    var updateBtnsLazy = document.getElementsByClassName('update-cart-lazy');
    var updateBtnsLazyLength = updateBtnsLazy.length;

    // Start the chain with a resolved promise
    var promiseChain = Promise.resolve();

    for (var i = 0; i < updateBtnsLazyLength; i++) {
        // Create a closure for each iteration
        (function (button) {
            var productId = button.dataset.product;
            var colorSizeId = button.dataset.color_size_id;
            var action = button.dataset.action;
            var quantity = button.value;

            if (parseInt(quantity) < 0) {
                action = "delete_item";
            }

            // Chain the promise for the current iteration
            promiseChain = promiseChain.then(() => {
                return updateUserOrder(productId, null, null, colorSizeId, action, quantity);
            });
        })(updateBtnsLazy[i]);
    }

    // Reload the location after all requests are completed
    promiseChain.then(() => {
        alert("سبد خرید بروز شد")
        location.reload();
    });
}

function updateUserOrder(productId, colorId, sizeId, colorSizeId, action, quantity, can_reload = false) {
    return fetch(updateOrderUrl, {
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
            if (can_reload) {
                location.reload();
            }
        })

}
