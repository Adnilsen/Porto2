function myFunction() {
    var x = document.getElementById("prev-btn");
    var y = document.getElementById("next-btn")
    if(x.style.visibility==="visible"){
        x.style.visibility = "hidden";
        y.style.visibility = "hidden";
    }else{
        x.style.visibility = "visible";
        y.style.visibility = "visible";
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



