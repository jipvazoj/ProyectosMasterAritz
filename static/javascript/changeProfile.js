(function(){

    // Password mismatching functionality
    window.onload = function(){
        document.getElementById("password1").addEventListener("keyup", validatePassword);
        document.getElementById("password2").addEventListener("keyup", validatePassword);
        document.getElementById("email").addEventListener("change", validateEmail);
        document.getElementById("username").addEventListener("change", validateUsername);
    };

    function validatePassword(){
        var pass2=document.getElementById("password2").value;
        var pass1=document.getElementById("password1").value;
        if(pass1.length==0){
            document.getElementById("password2").setCustomValidity('');
            return;
        }
        if(pass1.length>=6) {
            if (pass1 != pass2) {
                var passwordMissmatchMessage = document.getElementById("trans").dataset.passwordMissmatch;
                document.getElementById("password2").setCustomValidity(passwordMissmatchMessage);
            }
            else {
                document.getElementById("password2").setCustomValidity('');
            }
        }
        else{
            var passwordMinimumLengthMessage = document.getElementById("trans").dataset.passwordMinimumLength;
            document.getElementById("password2").setCustomValidity(passwordMinimumLengthMessage);
        }
    }

    function validateUsername(event){
        var input = event.target;
        var username = input.value;
        var initialUsername = document.getElementById('user-data').dataset.username;
        // User is not changed
        if(username==initialUsername){
            input.setCustomValidity('');
            return;
        }
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
        var initialEmail = document.getElementById('user-data').dataset.email;
        // Email is not changed
        if(email==initialEmail){
            input.setCustomValidity('');
            return;
        }
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