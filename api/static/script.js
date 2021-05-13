function myFunction(productID) {
    var x = document.getElementById(`prev-btn${productID}`);
    var y = document.getElementById(`next-btn${productID}`);
    var cardImage = document.getElementById(`product${productID}`).getElementsByTagName('img');

    if(cardImage[0].height === 170){
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


