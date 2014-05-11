(function() {
	"use strict";

	var api = angular.module('api', ['ngResource', 'ngCookies']);

	api.run(['$http', '$cookies', function($http, $cookies) {
		$http.defaults.headers.post['X-CSRFToken'] = $cookies['csrftoken'];
	}]);

	api.factory('Account', ['$resource', function($resource) {
		return $resource('/api/accounts/:id', {
			id: '@id'
		})
	}]);

	api.factory('User', ['$resource', function($resource) {
		return $resource('/api/users/:id', {
			id: '@id'
		}, {
			get: {
				method: 'GET',
				transformResponse: function(data, headers) {
					data = JSON.parse(data);
					data.account.balance = parseFloat(data.account.balance);
					return data;
				}
			}
		});
	}]);

	api.factory('Transaction', ['$resource', function($resource) {
		return $resource('/api/transactions/:id', {
			id: '@id'
		},{
			'query':  {
				method:'GET',
				isArray:false,
				transformResponse: function(data, headers){
					data = JSON.parse(data);
					var count = data.results.length;

					for(var i=0;i<count;i++) {
						data.results[i].date = moment(data.results[i].date).toDate();
						data.results[i].amount = parseFloat(data.results[i].amount);
					}
					return data;
				}
			}
		});
	}]);

	api.factory('CustomAction', ['$http', function($http) {

		return {
			'cashOut': function(email, amount) {
				return $http({
					url:'/api/account-cash-out',
					method: "GET",
					params: {
						'email': email,
						'amount': amount
					}
				});
			},
			'chargeCard': function( netAmount, chargeAmount, stripeToken) {
				return $http({
					url:'/api/charge-card',
					method: "GET",
					params: {
						'netAmount': netAmount, //without fee
						'chargeAmount': chargeAmount,
						'token': stripeToken
					}
				});
			}
		};
	}]);
}());
