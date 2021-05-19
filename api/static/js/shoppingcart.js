var products = []
var cartPrice = 0

function render_orders(data){ //renders all orders
    var order_table = document.getElementById("order_table")
    order_table.innerHTML=""
    for (i in data['products']){
        var row_amount = 0
        products[i] = data[i]
        //console.log(data['products'][i]['product_id']) //Hent brukere
        var row = `<tr class="order_row product" id="product${data['products'][i]['product_id']}">
                    <th scope="row">${parseInt(i)+1}</th>
                    <td class="product-images"><img src="static/images/${data['products'][i]['product_image']}" class="img-fluid" style="height: 150px;"></img></td>
                    <td><p class="fs-5">${data['products'][i]['product_name']}</p></td>
                    <td><p class="fs-5">${data['products'][i]['product_color']}</p></td>
                    <td><p class="fs-5 price-element">$${data['products'][i]['product_price']}</p></td>
                    <td>
                        <div class="d-flex mx-auto amount">
                            <div class="form-outline" style="width:40%">
                                <input type="number" id="typeNumber" class="form-control form-control-lg" value=${data['products'][i]['product_amount']} />
                                <label class="form-label" for="typeNumber">Number input</label>
                            </div>
                            <button type="button" class="btn btn-danger btn-sm">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </td>
                    </tr>`
        order_table.innerHTML += row
    }

    var inputOutline = document.querySelectorAll('.form-outline')
    inputOutline.forEach((formOutline) => { //init all input number fields (mdbootstrap)
        new mdb.Input(formOutline).init();
    });
    var numberInputs = document.getElementsByClassName("form-control")
    var removeCartItemButtons = document.getElementsByClassName("btn-danger")
    for(var i = 0; i < numberInputs.length; i++){
        var input = numberInputs[i]
        input.addEventListener('change', quantityChange)

        var button = removeCartItemButtons[i];
        button.addEventListener('click', function(event){
            removeProduct(event)
        })

    }
    updateCartPrice()

}

function removeProduct(event){
    var product_id = parseInt(event.target.parentElement.parentElement.parentElement.id.replace('product', ''))
    console.log(event.target.parentElement.parentElement.parentElement)
    console.log(product_id)
    if (isNaN(product_id)){
        product_id = parseInt(event.target.parentElement.parentElement.parentElement.parentElement.id.replace('product', ''))
        console.log(event.target.parentElement.parentElement.parentElement.parentElement)
        if (isNaN(product_id)){
            product_id = parseInt(event.target.parentElement.parentElement.id.replace('product', ''))
            console.log(event.target.parentElement.parentElement)
        }
    }
    console.log(product_id)
    fetch(`/order/current/delete/${product_id}`)
            .then(response => response.json())
            .then(data => {
                console.log(data)
                updatePage()
                update_cart_counter()
            })
    /*console.log("clicked")
    var buttonClick = event.target
    buttonClick.parentElement.parentElement.parentElement.remove()*/

    updateCartPrice()


}
function quantityChange(event){
    var input = event.target
    if(isNaN(input.value) || input.value <= 0){
        input.value = 1
    }
    updateCartPrice()
    updateOrderDb()
}

function updateCartPrice(){
    cartPrice = 0
    var priceColumns = document.getElementsByClassName("price-element")
    var numberInputs = document.getElementsByClassName("form-control")
    for(var i = 0; i < numberInputs.length; i++){
        var amount = numberInputs[i]
        var price = parseInt(priceColumns[i].innerText.replace('$', ''))
        cartPrice += amount.value * price
    }
    if(cartPrice > 0){
        document.getElementById("checkout").disabled = false
    }
    else{
        document.getElementById("checkout").disabled = true
    }
    var cartPriceItem = document.getElementById("cartPrice").innerText = '$' + cartPrice
}
function updateOrderDb(){
    var product_id = parseInt(event.target.parentElement.parentElement.parentElement.parentElement.id.replace('product', ''))
    var product_amount = parseInt(event.target.value)
    fetch(`/order/current/${product_id}/${product_amount}`)
        .then(response => response.json())
        .then(data => {
            console.log(data)
        })

}

function checkOut(){
    fetch("/order/checkout")
        .then(response => response.json())
        .then(data => {
            sessionStorage.setItem("orderCreated", false)
            showAlert(1, "You successfully finished an order. Store order number for later use!!")
            showReceipt()
            update_cart_counter()
        })
}

function showReceipt(){

    document.getElementById("orderInfo").className = "p-2"
    document.getElementById("orderLines").className = "p-2"
    document.getElementById("container").className = "container d-flex flex-row mb-3"
    document.getElementById("main_container").style = "margin-top: 180px"
    var random_order_id = Math.floor((Math.random() * 100) + 1);
    document.getElementById("title").innerHTML = `Your receipt <br>Order id: ${random_order_id} <button onclick="printReceipt()" id ="print" class="btn btn-primary">Print receipt</button>`
    document.getElementById("title").className = "text-center fs-1 fw-bold"
    var amount = document.getElementsByClassName("btn-danger")
    var inputField = document.getElementsByClassName("form-control")
    var containerAmount = document.getElementsByClassName("amount")
    document.getElementById("checkout").className= "d-none"
    var amount_length = amount.length
    for(var i = 0; i < amount_length; i++){
        console.log(i)
        var value = inputField[0].value
        inputField[0].remove()
        amount[0].remove()
        containerAmount[i].innerHTML = `<p class="fs-5">${value}</p>`
    }
}

function printReceipt(){
    document.getElementById("print").className += "d-none"
    window.print()
}

function updatePage(){
    fetch("/order/products")
        .then(response => response.json())
        .then(data => render_orders(data))
}


updatePage()