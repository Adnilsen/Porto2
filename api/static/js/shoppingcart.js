var user = []

function render_users(data){
    console.log("Her ja2")
    console.log(data)
    var order_table = document.getElementById("order_table")
    console.log(data['users'])
    for (i in data['users']){
        user[i] = data[i]
        console.log(data['users'][i]['name'])
        var row = `<tr class="order_row">
                    <th scope="row">${parseInt(i)+1}</th>
                    <td>${data['users'][i]['first_name']}</td>
                    <td>Amet</td>
                    <td>
                        <button type="button" class="btn btn-danger btn-sm px-3">
                        <i class="fas fa-times"></i>
                        </button>
                    </td>
                    <td>
                        <div class="container">
                            <div class="row">
                                <div class="col-md-3 d-flex">
                                    <div class="border align-items-center justify-content-center" style="height: 25px; margin-top: 15px;">
                                        <p>01</p>
                                    </div>

                                    <div>
                                        <button type="button" class="btn btn-primary btn-floating btn-sm">
                                            <i class="fas fa-angle-up"></i>
                                        </button>
                                        <button type="button" class="btn btn-primary btn-floating btn-sm">
                                            <i class="fas fa-angle-down"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </td>
                    </tr>`
        order_table.innerHTML += row
    }

}
function render_order(data){
    console.log("Her ja2")
    console.log(data)
    var order_table = document.getElementById("order_table")
    console.log(data['users'])
    for (i in data['users']){
        user[i] = data[i]
        console.log(data['users'][i]['name'])
        var row = `<tr class="order_row">
                    <th scope="row">${parseInt(i)+1}</th>
                    <td>${data['users'][i]['first_name']}</td>
                    <td>Amet</td>
                    <td>
                        <button type="button" class="btn btn-danger btn-sm px-3">
                        <i class="fas fa-times"></i>
                        </button>
                    </td>
                    </tr>`
        order_table.innerHTML += row
    }

}

fetch("/users")
    .then(response => response.json())
    .then(data => render_users(data))