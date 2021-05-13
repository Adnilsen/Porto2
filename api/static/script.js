function myFunction(productID) {
    var x = document.getElementById(`prev-btn${productID}`);
    var y = document.getElementById(`next-btn${productID}`);
    var cardImage = document.getElementById(`image${productID}`);
    /*var cardImage = document.getElementsByClassName("image" + productID);*/
    if(x.style.visibility==="visible"){
        x.style.visibility = "hidden";
        y.style.visibility = "hidden";
        cardImage.style.height = '120px';

    }else{
        x.style.visibility = "visible";
        y.style.visibility = "visible";
        cardImage.style.height = '170px';
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


