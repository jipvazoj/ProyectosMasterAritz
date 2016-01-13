(function(){
    function updateUsernameAndEmail(){
        var user_id = document.getElementById("userinfo").dataset.userId;

        var username = document.getElementById("username").value;
        var email = document.getElementById("email").value;
        $.post("/api/user/"+user_id+"/changeUserData/", {username:username, email:email}, function(data){
            if(data.result=="OK"){
                KaixoMundua.utils.okayResponseBox(document.getElementById("username"));
                KaixoMundua.utils.okayResponseBox(document.getElementById("email"));
            }
        },
        "json");
    }

    function requestProfileChange(){
        var user_id = document.getElementById("userinfo").dataset.userId;
        var emailSendMessage = document.getElementById('trans').dataset.emailSend;

        $.getJSON("/api/user/"+user_id+"/profileChangeRequest/",{}, function(data){
            if(data.result=="OK"){
                alert(emailSendMessage);
            }
            else{
                alert(data.data.error);
            }
        });
    }

    window.onload = function(){
        document.getElementById('username').addEventListener('change', updateUsernameAndEmail);
        document.getElementById('email').addEventListener('change', updateUsernameAndEmail);
        document.getElementById('requestChangeProfile').addEventListener('click', requestProfileChange);
    };
})();