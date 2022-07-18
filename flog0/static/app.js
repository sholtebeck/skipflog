'use strict';
var skipflog = angular.module('skipflog', []);

skipflog.controller('eventsController', ['$scope', '$http',
  function($scope, $http) {
   $http.get('/api/events.json').success(function(data) {
      $scope.events = data.events;
      $scope.event=data.events[0];
      $scope.players = $scope.event.players;
      $scope.pickers = data.pickers;
    });
    
   $scope.orderProp = '-Points';        

	$scope.setEvent = function()
    {
	  $scope.event = this.event;
      $scope.players = $scope.event.players;
	  $scope.pickers = $scope.event.pickers;
    };

 }]);
 
skipflog.controller('playersController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/players.json').success(function(data) {
      $scope.players = data.players;
      $scope.player = null;
    });         
    $scope.orderProp = 'POS';
	
	$scope.setPlayer = function(p)
    {
	  $scope.player = p;
      $scope.events = $scope.player.events;
      $scope.pickers = $scope.player.pickers;
    };

  }]);