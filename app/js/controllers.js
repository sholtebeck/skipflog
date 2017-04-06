'use strict';

/* Controllers */
var skipflog = angular.module('skipflog', []);

skipflog.controller('playersController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/players').success(function(data) {
      $scope.event = data.event;
      $scope.players = data.players;
     });
    $scope.orderProp = 'name';
    $scope.year = new Date().getFullYear();
  }]);

skipflog.controller('resultsController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/results?output=json').success(function(data) {
      $scope.event= data.results.event;
      $scope.players = data.results.players;
      $scope.pickers = data.results.pickers;
    });
    
    $scope.orderProp = 'Rank';
  }]);
