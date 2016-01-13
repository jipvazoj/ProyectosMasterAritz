(function(){
    function initMap(lat, lng) {
        map = new google.maps.Map(document.getElementById('map'), {
            center: {lat: lat, lng: lng},
            zoom: 13
        });
    }

    document.getElementById("searchInput").addEventListener("keypress", function(event){
        if (event.which == 13 || event.keyCode == 13) {
            var site = event.target.value;
            $.getJSON("/api/map/searchSite/?q="+site, {}, function(data){
                if(data.result=="OK"){
                    initMap(data.data.lat, data.data.lng);
                }
            });
        }
    });
    window.onload = function(){
        initMap(43.3183564,-1.981307);
    };

})();
