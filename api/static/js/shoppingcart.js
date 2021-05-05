var products = []
var cartPrice = 0

function render_orders(data){ //renders all orders
    var order_table = document.getElementById("order_table")
    for (i in data['products']){
        var row_amount = 0
        products[i] = data[i]
        console.log(data['products'][i]['product_name']) //Hent brukere
        var row = `<tr class="order_row">
                    <th scope="row">${parseInt(i)+1}</th>
                    <td class="w-25 product-image"></td>
                    <td><p class="fs-5">${data['products'][i]['product_name']}</p></td>
                    <td><p class="fs-5">${data['products'][i]['product_color']}</p></td>
                    <td><p class="fs-5 price-element">$${data['products'][i]['product_price']}</p></td>
                    <td>
                        <div class="d-flex mx-auto">
                            <div class="form-outline" style="width:40%">
                                <input type="number" id="typeNumber" class="form-control form-control-lg" value="1"/>
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
    var imageContainers = document.getElementsByClassName('product-image')
    for(var i = 0; i < numberInputs.length; i++){
        var input = numberInputs[i]
        input.addEventListener('change', quantityChange)

        var button = removeCartItemButtons[i];
        button.addEventListener('click', function(event){
            removeProduct(event)
        })

        var imageContainer = imageContainers[i]
        imageContainer.innerHTML = '<img src="static/images/ball1.png" class="img-fluid"></img>'
    }

    updateCartPrice()

}

function removeProduct(){
    console.log("clicked")
    var buttonClick = event.target
    buttonClick.parentElement.parentElement.parentElement.remove()
    updateCartPrice()
}
function quantityChange(event){
    var input = event.target
    if(isNaN(input.value) || input.value <= 0){
        input.value = 1
    }
    updateCartPrice()
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

    var cartPriceItem = document.getElementById("cartPrice").innerText = '$' + cartPrice
}


fetch("/order/1/products")
    .then(response => response.json())
    .then(data => render_orders(data))



