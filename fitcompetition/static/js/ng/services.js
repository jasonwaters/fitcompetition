(function() {
	"use strict";

	var api = angular.module('api', ['ngResource', 'ngCookies']);

	api.run(['$http', '$cookies', function($http, $cookies) {
		$http.defaults.headers.post['X-CSRFToken'] = $cookies['csrftoken'];
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

	api.factory('Transactions', ['$resource', function($resource) {
		return $resource('/api/transactions/:id', {
			id: '@id'
		}, {
			list: {
				method: 'GET',
				params: {
					page: 1
				},
				transformResponse: function(data, headers){
					data = JSON.parse(data);
					var count = data.results.length;

					for(var i=0;i<count;i++) {
						data.results[i].date = new Date(data.results[i].date);
						data.results[i].amount = parseFloat(data.results[i].amount);
					}
					return data;
				}
			}
		});
	}]);

	api.factory('CashOut', ['$resource', function($resource) {
		return $resource('/api/account-cash-out', {}, {
			go: {method: 'GET'}
		});
	}]);
}());
