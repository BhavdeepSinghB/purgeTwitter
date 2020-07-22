function checkURL() {
    if(window.location.search === "") {
        document.getElementsByClassName("Tokenization")[0].style.display = "none";
        document.getElementsByClassName("Main")[0].style.display = "block";
        return false;
    }
    document.getElementsByClassName("Tokenization")[0].style.display = "block";
    document.getElementsByClassName("Main")[0].style.display = "none";
    var str = window.location.search.split("&")[1].split("=")[1];
    document.getElementById("verifier_input").value = str;  
    return true;
}

function copyCode() {
    var copyText = document.getElementById("verifier_input");
    copyText.select();
    copyText.setSelectionRange(0, 99999);

    document.execCommand("copy");

    document.getElementById("copyBtn").innerHTML = "Copied!";
    document.getElementById("copyBtn").style.backgroundColor = "green";
    document.getElementById("copyBtn").style.color = "white";

}