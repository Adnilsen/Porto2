function myFunction(productID) {
    var x = document.getElementById(`prev-btn${productID}`);
    var y = document.getElementById(`next-btn${productID}`);
    var cardImage = document.getElementById(`product${productID}`).getElementsByTagName('img');
    var activeImage = document.getElementById(`product${productID}`).getElementsByClassName('active')[0].getElementsByTagName('img')[0];

    var products = document.getElementsByClassName('card');
    for(j=0; j<products.length; j++){

        if(j+1!==productID){
            products[j].getElementsByClassName('multi-collapse')[0].classList.remove('show');
            var productImages = products[j].getElementsByTagName('img');
            for(k=0; k<productImages.length; k++){
                productImages[k].style.height = '120px';
                products[j].getElementsByClassName('carousel-control-prev')[0].style.visibility = "hidden";
                products[j].getElementsByClassName('carousel-control-next')[0].style.visibility = "hidden";
            }
        }
    }

    if(activeImage.height === 170){
        x.style.visibility = "hidden";
        y.style.visibility = "hidden";
        for(i = 0; i<cardImage.length; i++){
            cardImage[i].style.height = '120px';
        }
    }else{
        if(cardImage.length===1){
            x.style.visibility = "hidden";
            y.style.visibility = "hidden";
            cardImage[0].style.height = '170px';
        }else {
            x.style.visibility = "visible";
            y.style.visibility = "visible";
            for (i = 0; i < cardImage.length; i++) {
                cardImage[i].style.height = '170px';
            }
        }
    }
}
function showAlert(){
    console.log("ja")
    var alertElement = document.getElementById("alert")
    alertElement.classList.remove("d-none")
    setTimeout(function(){
    alertElement.classList.add("d-none")
  },8000)
}
function update_cart_counter(){
     fetch("/order/count")
            .then(response => response.json())
            .then(data => {
                console.log
            })
    var counter = document.getElementById("shopping_counter")
    counter.innerHTML = 2
}


