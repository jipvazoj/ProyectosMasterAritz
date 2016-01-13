(function(){
    function requestForgottenPassword(){
        var username = document.getElementById('username').value;
        if(username==""){
            KaixoMunduaUtils.errorResponseBox(document.getElementById('username'));
        }
        else{
            $.get("/recover/"+username, {}, function(data){
                if(data.result=="OK"){
                    var emailSendMessage = document.getElementById('trans').dataset.emailSend;
                    alert(emailSendMessage);
                }
            });
        }
    }

    window.onload = function(){
        document.getElementById('forgottenPassword').addEventListener('click', requestForgottenPassword);
    }
})();