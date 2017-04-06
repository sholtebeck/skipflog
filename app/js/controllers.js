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
    $http.get('/api/results').success(function(data) {
      $scope.results= data.results;
      $scope.pickers = data.pickers;
    });
    
    $scope.orderProp = 'Rank';
  }]);
