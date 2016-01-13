/**
 * Created by Haritz on 22/12/2015.
 */

(function(){
    window.onload = function(){

        Dropzone.autoDiscover = false;

        function createNewDropzone(){
            // Request blob upload url to GAE and create dropzone uploader
            $.ajax({
                dataType: "json",
                url: "/api/photos/upload/path",
                data: {},
                success: function(data){
                    var dropzone = new Dropzone("div#photo-dropzone", {
                        url: data.data.url,
                        acceptedFiles: "image/*",
                        clickable: true,
                        success: function(uploader, response){
                            // Show image on page
                            var imageId = response.data.photo_id;
                            showImage(imageId);
                            // Change dropzone url
                            dropzone.destroy();
                            createNewDropzone();
                        }
                    });
                }
            });
        }

        function showImage(photo_id){
            // Create link
            var link = document.createElement('a');
            link.href = "/photo/"+photo_id;
            link.classList.add("photoLink")
            // Create div
            var div = document.createElement('div');
            div.classList.add("imageRectangle");
            // Create image
            var img = document.createElement('img');
            img.src = "/api/photo/download/"+photo_id;
            img.classList.add("photo");
            // Append image to container
            div.appendChild(img);
            // Append container to link
            link.appendChild(div);
            // Append to container
            var container = document.getElementById('photosContainer');
            container.insertBefore(link, container.firstChild);
        }

        /* Create the dynamic content */

        // File uploader: Check if user can upload images, and create a dropzone for it
        var dropzone = document.getElementById("photo-dropzone");
        if(dropzone){
            createNewDropzone();
        }

        // Photos visualization
        // Retrieve all photos
        $.getJSON("/api/photos/manage/list", {}, function(data){
            var photos = data.data.photos;
            for(var i=0;i<photos.length;i++){
                photo = photos[i];
                showImage(photo.photo_id);
            }
        });


    };
})();

