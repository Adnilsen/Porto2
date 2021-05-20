function addToCart(){
    sessionStorage.setItem("firstStartup", false)
    var button = event.target
    var cardElement = button.parentElement.parentElement.parentElement
    var productId = cardElement.id.replace('product', '')
    console.log(productId)
    if(sessionStorage.getItem("loggedInn") == "false"){
        showAlert(0, "You have to log in to add products to cart")
    }
    else{
        if(sessionStorage.getItem("orderCreated") == "true"){
            //Legg til produkter
            console.log("HEEER")
            fetch(`/order/current/${productId}`)
            .then(response => response.json())
            .then(data => {
                if(data = true){
                    showAlert(1, "An item was added to the cart")
                    update_cart_counter()
                }
            })
            console.log("Ordre er laget")

        }
        else{ //Lag ordre og legg til produkt
            fetch("/order")
            .then(response => response.json())
            .then(data => {
                sessionStorage.setItem("orderCreated", data)
                fetch(`/order/current/${productId}`)
                .then(response => response.json())
                .then(data => {
                    if(data = true){
                        showAlert(1, "An order has been created and an item was added to the cart")
                        update_cart_counter()
                    }
                })
            })
        }
    }
}


function isUnfinishedOrder(){
    fetch("/order/unfinished/0")
        .then(response => response.json())
        .then(data => {
            console.log("knapp")
            if(data){
                console.log(data)
                document.getElementById("btnAlert").click()
            }
        })
}

function retrieveLastOrder(){
    sessionStorage.setItem("firstStartup", false)
    fetch("/order/unfinished/1")
    .then(response => response.json())
    .then(data => {
        console.log("Update")
        update_cart_counter()
        sessionStorage.setItem("orderCreated", data)
    })
}

function deleteLastOrder(){
    sessionStorage.setItem("firstStartup", false)
    fetch("/order/delete")
    .then(response => response.json())
    .then(data => {
        console.log(data)
        console.log("deleted")
        update_cart_counter()
    })
}


window.addEventListener('load', (event) => {
    fetch("/loggedInn")
            .then(response => response.json())
            .then(data => {
                sessionStorage.setItem("loggedInn", data)
                if(sessionStorage.getItem("firstStartup") == "true"){
                    if(sessionStorage.getItem("loggedInn") == "true"){
                        console.log("her2")
                        isUnfinishedOrder()
                        update_cart_counter()
                    }
                }
            })
});

