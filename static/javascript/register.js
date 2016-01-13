(function(){

    // Password mismatching functionality
    window.onload = function(){
        document.getElementById("password1").addEventListener("keyup", validatePassword);
        document.getElementById("password2").addEventListener("keyup", validatePassword);
        document.getElementById("email").addEventListener("change", validateEmail);
        document.getElementById("username").addEventListener("change", validateUsername);
    }

    function validatePassword(){
        var pass2=document.getElementById("password2").value;
        var pass1=document.getElementById("password1").value;
        if(pass1!=pass2){
            var messageToDisplay = document.getElementById("trans").dataset.passwordMissmatch;
            document.getElementById("password2").setCustomValidity(messageToDisplay);
        }
        else{
            document.getElementById("password2").setCustomValidity('');
        }
    }

    function validateUsername(event){
        var input = event.target;
        var username = input.value;
        $.getJSON("/api/register/userExists/?q="+username, {}, function(data){
            if(data.result=="OK"){
                if(data.data.exists){
                    var messageToDisplay = document.getElementById("trans").dataset.usernameUsed;
                    input.setCustomValidity(messageToDisplay);
                }
                else{
                    input.setCustomValidity('');
                    document.getElementById("errorMessage").innerHTML = "";
                }
            }
        });
    }

    function validateEmail(event){
        var input = event.target;
        var email = input.value;
        $.getJSON("/api/register/emailExists/?q="+email, {}, function(data){
            if(data.result=="OK"){
                if(data.data.exists){
                    var messageToDisplay = document.getElementById("trans").dataset.emailUsed;
                    input.setCustomValidity(messageToDisplay);
                }
                else{
                    input.setCustomValidity('');
                }
            }
        });
    }

})();