var likeBtns = document.getElementsByClassName('like-product')

for (var i = 0; i < likeBtns.length; i++) {
    likeBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product

        likeProduct(productId, productLikeUrl)
    })
}
function likeProduct(productId, url) {

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId})
    })


        .then((response) => {
            console.log('data')
            return response.json();
        })

        .then((data) => {
            console.log('data', )

            if(data['authenticated'] === false){
                window.location.href = data['login']
            }
            else{
                location.reload()
            }

        })
}

