'use strict';
var skipflog = angular.module('skipflog', []);

skipflog.controller('picksController', ['$scope', '$http',
function($scope, $http) {
  $http.get('/api/picks').success(function(data) {
    $scope.event_name = data.event_name;
    $scope.picks = data.picks;
  }
);
  
 
  
  $scope.dropPlayer = function()
  {
    console.log("dropping "+ this.player);
    $http.post("/player/drop", { player: this.player })
    .success(function(data, status, headers, config) {
                 $scope.message=data.message;
                 if (data.success) {
                         $http.get('/api/event').success(function(data)  {   $scope.pickers = data.pickers });
                       } 
                      }).error(function(data, status, headers, config) {});
  };
}]);

skipflog.controller('eventsController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/event').success(function(data) {
      $scope.players = data.players;
      $scope.pickers = data.pickers;
      $scope.pick_no = data.pick_no;
      $scope.results = data.results;
    });
    
   $scope.orderProp = '-Points';
   $http.get('/api/events').success(function(data) {
      $scope.events = data.events;
	    $scope.event_id = data.event_id;
      $scope.event = data.events[0];
    });         

	$scope.setEvent = function()
    {
	  $scope.event = this.event;
      $http.get('/api/event/'+ $scope.event.event_id ).success(function(data) {
			$scope.players = data.players;
			$scope.pickers = data.pickers;
      $scope.results = data.results;
		});
    };

    $scope.pickPlayer = function()
    {
      //console.log("picking "+ this.player.name);
      $http.post("/api/pick", { player: this.player.name })
      .success(function(data, status, headers, config) {
                     if (data.success) {
                          $http.get('/api/event').success(function(data)  {   
                            $scope.pickers = data.pickers 
                            $scope.players = data.players
                          });
                            } 
                        }).error(function(data, status, headers, config) {});
    };   
    

  }]);