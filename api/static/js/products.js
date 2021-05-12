
function addToCart(){
    var button = event.target
    var cardElement = button.parentElement.parentElement.parentElement
    var productId = cardElement.id.replace('product', '')
    console.log(productId)
    if(sessionStorage.getItem("orderCreated") == "true"){
        //Legg til produkter
        console.log("HEEER")
        fetch(`/order/current/${productId}`)
        .then(response => response.json())
        .then(data => {
            if(data = true){
                showAlert()
            }
        })
        console.log("Ordre er laget")

    }
    else{ //Lag ordre og legg til produkt
        console.log("hey")
        fetch("/order")
        .then(response => response.json())
        .then(data => {
            sessionStorage.setItem("orderCreated", data)
            fetch(`/order/current/${productId}`)
            .then(response => response.json())
            .then(data => {
                if(data = true){
                    showAlert()
                }
            })
        })
    }
    update_cart_counter()
}


