KaixoMunduaUtils = {};

KaixoMunduaUtils.okayResponseBox = function(domElement){
    green();
    setTimeout(blank, 3000);
    function green(){
        KaixoMunduaUtils.setBackgroundColor(domElement, "green");
    }

    function blank(){
        KaixoMunduaUtils.setBackgroundColor(domElement, "white");
    }
};

KaixoMunduaUtils.errorResponseBox = function(domElement){
    red();
    setTimeout(blank, 3000);
    function red(){
        KaixoMunduaUtils.setBackgroundColor(domElement, "red");
    }
    function blank(){
        KaixoMunduaUtils.setBackgroundColor(domElement, "white");
    }
};

KaixoMunduaUtils.setBackgroundColor = function(domElement, color){
    domElement.style.backgroundColor = color;
};