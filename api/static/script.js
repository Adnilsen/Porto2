function showAlert(){
    console.log("ja")
    var alertElement = document.getElementById("alert")
    alertElement.classList.remove("d-none")
    setTimeout(function(){
    alertElement.classList.add("d-none")
  },8000)
}



