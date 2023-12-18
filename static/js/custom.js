var updateBtns = document.getElementsByClassName('update-cart');
var colorButtons = document.getElementsByClassName('color-button');
var sizeButtons = document.getElementsByClassName('size-button');
var sizeButtonsSelector = document.querySelectorAll('.size-button');
var qtyInput = document.getElementById("qty");
var buttonQtyPlus = document.getElementsByClassName("updateQtyPlus");
var buttonQtyMinus = document.getElementsByClassName("updateQtyMinus");
var selectedColorId = null;
var selectedSizeId = null;


// Event listener for color buttons
for (var i = 0; i < colorButtons.length; i++) {
    colorButtons[i].addEventListener('click', function () {
        // Update the data-color-id attribute of the "Add to Cart" button
        var updateCart = 'update-cart-' + this.dataset.product
        var updateCartMini = 'update-cart-' + this.dataset.product + '-mini'
        var updateCartArray = [updateCart, updateCartMini]
        for (i = 0; i < updateCartArray.length; i++) {
            var addToCartButton = document.querySelector('.' + updateCartArray[i] + '[data-product="' + this.dataset.product + '"]');
            if (addToCartButton) {
                addToCartButton.dataset.colorId = this.dataset.colorId;
                console.log('Updated Color ID on Add to Cart button:', addToCartButton.dataset.colorId);
            }
        }
        // Store the selected color ID
        selectedColorId = this.dataset.colorId;
        console.log('Selected Color ID:', selectedColorId);

        // Get data attributes from the button
        var productId = this.dataset.product;
        var colorId = this.dataset.colorId;
        console.log('this is the data: ', productId, 'color', colorId,)
        // Your AJAX request
        filterSize(productId, colorId)
    });
}

// Event listener for size buttons
for (var i = 0; i < sizeButtons.length; i++) {
    sizeButtons[i].addEventListener('click', function () {
        // Update the data-size-id attribute of the "Add to Cart" button
        var updateCart = 'update-cart-' + this.dataset.product
        var updateCartMini = 'update-cart-' + this.dataset.product + '-mini'
        var updateCartArray = [updateCart, updateCartMini]

        for (i = 0; i < updateCartArray.length; i++) {
            console.log(updateCartArray)
            console.log('this is result', '.' + updateCartArray[i] + '[data-product="' + this.dataset.product + '"]')
            var addToCartButton = document.querySelector('.' + updateCartArray[i] + '[data-product="' + this.dataset.product + '"]');
            if (addToCartButton) {
                addToCartButton.dataset.sizeId = this.dataset.sizeId;
                console.log('Updated Size ID on Add to Cart button:', addToCartButton.dataset.sizeId);
            }
        }
        // Store the selected size ID
        selectedSizeId = this.dataset.sizeId;
        console.log('Selected Size ID:', selectedSizeId);
    });
}

function updateSizeButtons(productId) {
    for (var i = 0; i < sizeButtons.length; i++) {
        var sizeButton = sizeButtonsSelector[i];
        var sizeButtonId = sizeButton.id;
        var sizeProductId = sizeButton.dataset.product;
        var sizeId = sizeButton.dataset.sizeId;
        var colorId = sizeButton.dataset.colorId;

        // Show the size button only if it matches the selected product and color or if no color is selected
        if ((sizeProductId === productId) && (!selectedColorId || colorId === selectedColorId)) {
            document.getElementById(sizeButtonId).style.display = 'block';
        } else {
            document.getElementById(sizeButtonId).style.display = 'none';
        }
    }
}

function filterSize(productId, colorId) {
    $.ajax({
        url: filterSizeUrl,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        data: JSON.stringify({
            'productId': productId,
            'colorId': colorId,
        }),
        cache: false,
        processData: false,
        contentType: false,

        success: function (response) {

            // Extract the size IDs from the response
            var sizeIdsToShow = Array.isArray(response.sizeIds) ? response.sizeIds : [];


            // Get all size buttons for the current product
            var productSizeButtons = document.getElementsByClassName('size-button-' + productId);

            // Loop through each size button
            for (var i = 0; i < productSizeButtons.length; i++) {
                var sizeButton = productSizeButtons[i];
                var sizeId = sizeButton.dataset.sizeId;

                // Check if the size ID is in the list of IDs to show
                if (sizeIdsToShow.includes(sizeId)) {
                    // If the size ID is in the list, show the button
                    sizeButton.style.display = 'inline-block';  // You can adjust the display style as needed
                } else {
                    // If the size ID is not in the list, hide the button
                    sizeButton.style.display = 'none';  // You can adjust the display style as needed
                }
            }
        },

        error: function (error) {
            // Handle error
            console.log(error);
        }
    });
}

// Wait for the document to be ready
$(document).ready(function () {
    // Color selection
    $('.color-button').on('click', function () {
        // Remove the 'selected' class from all color buttons
        $('.color-button').removeClass('selected');
        console.log('correct')
        // Add the 'selected' class to the clicked color button
        $(this).addClass('selected');
    });

    // Size selection
    $('.size-button').on('click', function () {
        // Remove the 'selected' class from all size buttons
        $('.size-button').removeClass('selected');
        console.log('correct')

        // Add the 'selected' class to the clicked size button
        $(this).addClass('selected');
    });
});