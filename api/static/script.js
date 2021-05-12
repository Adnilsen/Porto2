function myFunction(productID) {
    var x = document.getElementById(`prev-btn${productID}`);
    var y = document.getElementById(`next-btn${productID}`);
    var cardImage = document.getElementById(`product${productID}`).getElementsByTagName('img');
    if(x.style.visibility==="visible"){
        x.style.visibility = "hidden";
        y.style.visibility = "hidden";
        cardImage.style.height = "120px";
    }else{
        x.style.visibility = "visible";
        y.style.visibility = "visible";
        cardImage.style.height = "150px";
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
    var counter = document.getElementById("shopping_counter")
    counter.innerHTML = 2
}



