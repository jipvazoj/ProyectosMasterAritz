(function(){
    window.onload = function(){
        // Add photo properties modification event handlers
        document.getElementById('nameInput').addEventListener('change', uploadChanges);
        var privacyLevelSelector = document.getElementById('privacySelector');
        privacyLevelSelector.addEventListener('change', uploadChanges);
        document.getElementById('delete').addEventListener('click', deleteImage);
        document.getElementById('setAsBackground').addEventListener('click', setAsBackground);
        document.getElementById('setAsProfilePhoto').addEventListener('click', setAsProfilePhoto);
        // Add restricted user permission panel event handlers
        document.getElementById('restrictedUserAdder').addEventListener('click', addRestrictedUserPermission);
        var usersToRemove = document.getElementsByClassName('restrictedUserRemover');
        for(var i=0;i<usersToRemove.length;i++){
            var restrictedUserRemover = usersToRemove[i];
            restrictedUserRemover.addEventListener('click', removeRestrictedUserPermission);
        }
        // Visualization options depending on privacy level handler
        privacyLevelSelector.addEventListener('change', displayRestrictedUserPanelConfiguration);
        // Restricted user privacy panel show if privacy level is restricted users
        if(privacyLevelSelector.value==1){
            document.getElementById('restrictedUserBox').style.display = "block";
        }

    };

    // Privacy: allow/give permisson to user
    function addRestrictedUserPermission(event){
        var userId = document.getElementById('restrictedUserSelector').value;
        var username = $( "#restrictedUserSelector option:selected" ).text();
        var photoId = document.getElementById('photo').dataset.photoId;
        if(userId != null && photoId != null){
            $.getJSON("/api/photos/permission/"+photoId+"/"+userId+"/give",{}, function(data){
                if(data.result=="OK"){
                    var div = document.createElement("div");
                    div.classList.add('allowedUsers');
                    div.id = "allowed_user_"+userId;
                    div.dataset.userId = userId;
                    // Create user anchor and img to delete
                    var link = document.createElement("a");
                    link.href = "/profile/"+userId;
                    link.textContent = username;
                    var img = document.createElement('img');
                    img.src = "/images/remove.png";
                    img.classList.add("restrictedUserRemover");
                    img.addEventListener('click', removeRestrictedUserPermission);
                    div.appendChild(link);
                    div.appendChild(img);
                    document.getElementById("allowed_users").appendChild(div);
                }
            });
        }
    }
    // Privacy: restrict permisson to user
    function removeRestrictedUserPermission(event){
        debugger;
        var userId = event.target.parentNode.dataset.userId;
        var photoId = document.getElementById('photo').dataset.photoId;
        if(userId != null && photoId != null){
            $.getJSON("/api/photos/permission/"+photoId+"/"+userId+"/restrict",{}, function(data){
                if(data.result=="OK"){
                    $("#allowed_user_"+userId).remove();
                }
            });
        }
    }


    function displayRestrictedUserPanelConfiguration(event){
        var privacyLevel = event.target.value;
        var panel = document.getElementById('restrictedUserBox');
        if(privacyLevel==1){
            panel.style.display = "block";
        }
        else{
            panel.style.display  = "none";
        }
    }


    // Modify ajax function
    function uploadChanges(event){
        var photo_id = document.getElementById('photo').dataset.photoId;
        var name = document.getElementById('nameInput').value;
        var privacy = document.getElementById('privacySelector').value;
        $.post("/api/photo/modify/"+photo_id, {name: name, privacy: privacy}, function(data){
            // TODO show result to user
            console.log(data);
        }, "json");
    }

    function deleteImage(event){
        var messageToDisplay = document.getElementById("trans").dataset.wantToDelete;
        // Ask user if want to delete image
        if(confirm(messageToDisplay)){
            var photo_id = document.getElementById('photo').dataset.photoId;
            $.get("/api/photo/delete/"+photo_id, function(data){
                if(data.result=="OK"){
                    window.location = "/photos";
                }
                else{
                    // Show error to user
                    alert(data.data.message);
                }
            });
        }
    }

    function setAsBackground(event){
        var messageToDisplay = document.getElementById("trans").dataset.setAsBackground;
        if(confirm(messageToDisplay)){
            var photo_id = document.getElementById('photo').dataset.photoId;
            var user_id = document.getElementById("userinfo").dataset.userId;
            $.post("/api/user/"+user_id+"/changeUserData/", {background: photo_id}, function(data){
                window.location.reload(false);
            })
        }
    }

    function setAsProfilePhoto(event){
        var messageToDisplay = document.getElementById("trans").dataset.setAsProfilePhoto;
        if(confirm(messageToDisplay)){
            var photo_id = document.getElementById('photo').dataset.photoId;
            var user_id = document.getElementById("userinfo").dataset.userId;
            $.post("/api/user/"+user_id+"/changeUserData/", {photo: photo_id}, function(data){
                console.log(data);
            })
        }
    }
})();