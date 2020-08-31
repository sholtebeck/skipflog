/**
 * Copyright 2018, Google LLC
 * Licensed under the Apache License, Version 2.0 (the `License`);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an `AS IS` BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

// [START gae_python38_auth_javascript]
window.addEventListener('load', function () {
  document.getElementById('sign-out').onclick = function () {
    firebase.auth().signOut();
  };

  // FirebaseUI config.
  var uiConfig = {
    signInSuccessUrl: '/',
    signInOptions: [
      // Comment out any lines corresponding to providers you did not check in
      // the Firebase console.
      firebase.auth.GoogleAuthProvider.PROVIDER_ID,
      firebase.auth.EmailAuthProvider.PROVIDER_ID,
      //firebase.auth.FacebookAuthProvider.PROVIDER_ID,
      //firebase.auth.TwitterAuthProvider.PROVIDER_ID,
      //firebase.auth.GithubAuthProvider.PROVIDER_ID,
      //firebase.auth.PhoneAuthProvider.PROVIDER_ID

    ],
    // Terms of service url.
    tosUrl: '<your-tos-url>'
  };

  firebase.auth().onAuthStateChanged(function (user) {
    if (user) {
      // User is signed in, so display the "sign out" button and login info.
      document.getElementById('sign-out').hidden = false;
      document.getElementById('login-info').hidden = false;
      console.log(`Signed in as ${user.displayName} (${user.email})`);
      user.getIdToken().then(function (token) {
        // Add the token to the browser's cookies. The server will then be
        // able to verify the token against the API.
        // SECURITY NOTE: As cookies can easily be modified, only put the
        // token (which is verified server-side) in a cookie; do not add other
        // user information.
        document.cookie = "token=" + token;
      });
    } else {
      // User is signed out.
      // Initialize the FirebaseUI Widget using Firebase.
      var ui = new firebaseui.auth.AuthUI(firebase.auth());
      // Show the Firebase login button.
      ui.start('#firebaseui-auth-container', uiConfig);
      // Update the login state indicators.
      document.getElementById('sign-out').hidden = true;
      document.getElementById('login-info').hidden = true;
      // Clear the token cookie.
      document.cookie = "token=";
    }
  }, function (error) {
    console.log(error);
    alert('Unable to log in: ' + error)
  });
});
// [END gae_python38_auth_javascript]

var skipflog = angular.module('skipflog', []);
skipflog.controller('eventsController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/events').success(function(data) {
      $scope.events = data.events;
      $scope.event_id = data.event_id;
    });  
    $scope.orderProp = '-event_id';
	$scope.setEvent = function()
    {
      alert("setting "+ this.Event.event_name );
	  $scope.event_id = this.Event.event_id;
      $http.post("/api/events", { "event_id": $scope.event_id });
    };
  }]);

knarflog.controller('eventController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/api/event').success(function(data) {
      $scope.pickers = data.pickers;
	  $scope.players = data.players;
    });
    
     $scope.pickPlayer = function()
    {
      alert("picking "+ this.player);
      $http.post("/pick", { player: this.player })
      .success(function(data, status, headers, config) {
                     $scope.message=data.message;
                     if (data.success) {
                          $http.get('/api/event').success(function(data)  {   
						        $scope.picks = data.picks;
                                $scope.players=data.players;								
								});
                            } 
                        }).error(function(data, status, headers, config) {});
    };   
    
	$scope.setEvent = function()
    {
	  $scope.Event = this.event;
      $http.get('/api/event/'+ $scope.Event.event_id ).success(function(data) {
			$scope.headers = data.headers;
			$scope.players = data.players;
			$scope.pickers = data.pickers;
		});
    };
	
  }]);