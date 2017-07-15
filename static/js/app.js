//declare a variable for my categories
var Category = function(id, name) {
    this.categoryId = id;
    this.catText = name;
};
//Fetch relevant map icons from google

var iconBase = 'https://maps.google.com/mapfiles/kml/shapes/';
var icons = {
    artisan: {
        icon: iconBase + 'man.png'
    }
};


//create the map and the view model
function initMap() {
    var ViewModel = function() {
        var self = this;
        var lat = -1.2886009200028272;
        var lng = 36.822824478149414;
        var infowindow;
        self.artLocations = new ko.observableArray();
        self.markers = new ko.observableArray();
        self.catId = ko.observable('');
        self.categoryTips = new ko.observableArray();
        self.categories = new ko.observableArray();

        self.map = new google.maps.Map(document.getElementById('map'), {
            zoom: 16,
            center: new google.maps.LatLng(lat, lng),
            mapTypeId: 'roadmap'
        });

        // fetch artisan details and locations from the database and store them in array artLocations

        var xhttp;
        xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            var i;
            if (this.readyState === 4 && this.status === 200) {
                var myText = this.responseText;
                var obj = JSON.parse(myText);
                var myAdd = {};
                var addresses = obj.Addresses;
                var l = addresses.length;
                for (i = 0; i < l; i++) {
                    myAdd = {
                        position: {
                            lat: parseFloat(obj.Addresses[i].lat),
                            lng: parseFloat(obj.Addresses[i].lng)
                        },
                        name: obj.Addresses[i].name,
                        skill: obj.Addresses[i].skill,
                        cat: obj.Addresses[i].cat,
                        bio: obj.Addresses[i].bio,
                        id: obj.Addresses[i].id,
                        details: obj.Addresses[i].details,
                        type: 'artisan'
                    };

                    self.artLocations().push(myAdd);

                }
                var c = obj.Categories.length;
                for (i = 0; i < c; i++) {
                    self.categories().push(new Category(obj.Categories[i].id, obj.Categories[i].name));

                }
                // Iterate over artisan details and locations and create map markers and store them in markers array
                self.artLocations().forEach(function(feature) {
                    infowindow = new google.maps.InfoWindow({
                        content: ''
                    });
                    var marker = new google.maps.Marker({
                        position: feature.position,
                        icon: icons[feature.type].icon,
                        title: feature.name,
                        cat: feature.cat,
                        bio: feature.bio,
                        id: feature.id,
                        skill: feature.skill


                    });
                    // include an info window on click for each marker with artisan details and link to respective list item
                    marker.addListener('click', showWindow = function() {
                        marker = this;
                        var content = this.skill + '<br>' + this.bio + '<a href="/show/artisan/' + this.id + '">' + '<br>' + 'Click for More' + '</a>';
                        if (infowindow) {
                            infowindow.close();
                        }
                        infowindow.setContent(content);
                        infowindow.open(self.map, marker);
                        marker.setAnimation(google.maps.Animation.BOUNCE);
                        setTimeout(function() {
                            marker.setAnimation(null);
                        }, 2100);
                    });
                    self.markers.push(marker);
                });
            } else if (this.readyState === 4) {

                var pos = {
                    lat: lat,
                    lng: lng
                };

                var infoWindow = new google.maps.InfoWindow({
                    map: self.map
                });
                infoWindow.setPosition(pos);
                infoWindow.setContent('An error occured, we are unable to retreive Artisan Locations.');

            }
            // Function to set the map on all markers in the array if it is not empty.
            function displayMarkers(map) {
                if (self.markers().length > 0) {
                    for (i = 0; i < self.markers().length; i++) {
                        self.markers()[i].setMap(map);
                    }
                }
            }
            // Function to remove the markers from the map, but keeps them in the array.
            function clearMarkers() {
                displayMarkers(null);
            }

            //actually display all markers on the map then store them in allMarkers array for when we start manipulating the markers


            displayMarkers(self.map);
            var allMarkers = self.markers();



            //filter the markers depending on the category of artisans selected

            var updatedMarkers = [];

            self.catId.subscribe(function(newId) {
                clearMarkers();

                if (newId === '') {
                    updatedMarkers = allMarkers;
                } else {
                    for (i = allMarkers.length - 1; i >= 0; i--) {
                        if (allMarkers[i].cat === newId) {
                            updatedMarkers.push(allMarkers[i]);
                        }
                    }
                }

                //display filtered markers by calling calling out observable array with array of filtered markers. Reset updatedMarkers
                self.markers(updatedMarkers);
                displayMarkers(self.map);
                updatedMarkers = [];
            });

        };

        xhttp.open('GET', '/loc', true);
        xhttp.send();




        self.catId.subscribe(function(newId) {
            var catText = 'Do it Yourself - DIY';
            var x;
            for (x = 0; x < self.categories().length; x++) {
                if (self.categories()[x].categoryId === newId) {
                    catText = self.categories()[x].catText;
                }
            }

            var nyttp;
            nyttp = new XMLHttpRequest();
            nyttp.onreadystatechange = function() {
                var updatedLinks = [];
                var link;
                if (this.readyState === 4 && this.status === 200) {

                    var myResponse = this.responseText;
                    var obj = JSON.parse(myResponse);
                    var i;
                    var articles = obj.response.docs;
                    var l = articles.length - 4;
                    var headline;
                    var url;
                    for (i = 0; i < l; i++) {
                        headline = articles[i].headline.main;
                        url = articles[i].web_url;
                        link = '<a href="' + url + '">' + headline + '</a>';
                        updatedLinks.push(link);

                    }
                    self.categoryTips(updatedLinks);
                } else if (this.readyState === 4) {
                    link = '<a href="https://www.nytimes.com/">An error occured, we are unable to retrieve NYT tips but you can click here to explore their website</a>';
                    updatedLinks.push(link);
                    self.categoryTips(updatedLinks);
                    updatedLinks = [];
                }
            };
            var nytUrl = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?q=' + catText + '&api-key=440fb4e8ca6a45da863a6e7152f51571';
            nyttp.open('GET', nytUrl, true);
            nyttp.send();
        });

    };
    ko.applyBindings(new ViewModel());

}