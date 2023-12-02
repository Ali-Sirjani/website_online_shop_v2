var updateBtns = document.getElementsByClassName('update-cart')

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var colorId = this.dataset.colorId
        var sizeId = this.dataset.sizeId
        var colorSizeId = this.dataset.color_size_id
        var action = this.dataset.action
        var quantityInput = document.getElementById('qty');
        var quantity = quantityInput ? quantityInput.value : 1;

        if (!(action === 'delete_item' || action === 'delete_cart')) {
            var intQtyInput = parseInt(quantity)
            if (intQtyInput > 0) {
                action = 'add';
                console.log('this is add')
            } else if (intQtyInput < 0) {
                action = 'remove';
            } else {
                action = '';
            }
        }

        updateUserOrder(productId, colorId, sizeId, colorSizeId, action, quantity)
    })
}

function updateUserOrder(productId, colorId, sizeId, colorSizeId, action, quantity) {
    console.log('user log in', colorSizeId)

    var url = 'http://127.0.0.1:8000/products/cart/update-item/'

    fetch(url, {
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
            console.log('data')
            return response.json()
        })

        .then((data) => {
            console.log('data', data)
            location.reload()
        })

}