(function() {
	"use strict";

	function summarize(items) {
		return _.reduce(items, function(result, item) {
			return result + item['value'];
		},0);
	}

	var modals = angular.module('modals', ['api', 'ui.bootstrap', 'angularPayments']);

	modals.controller('cash-out-modal-controller', ['$scope', '$modalInstance', function ($scope, $modalInstance) {
		$scope.accountBalance = FC.account.balance;
		$scope.details = {
			email: '',
			amount: null
		};

		$scope.ok = function () {
			$modalInstance.close($scope.details);
		};

		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};
	}]);

	modals.controller('deposit-funds-modal-controller', ['$scope','$modalInstance','modalFactory','lineItems', 'CustomAction', function ($scope, $modalInstance, modalFactory, lineItems, CustomAction) {
		var subTotal = summarize(lineItems);
		var transactionFee = (subTotal*0.029)+0.30;
		transactionFee = Math.round(transactionFee*100)/100; //round to two decimal places

		lineItems.push(modalFactory.createLineItem("Transaction Fee", transactionFee, "Transaction fees apply only when you put money in the pot."));
		$scope.lineItems = lineItems;
		$scope.totalCost = summarize($scope.lineItems);
		$scope.number = '4242424242424242';

		$scope.handleStripe = function(status, response){
			$scope.errorMessage = null;
			$scope.submitting = true;

			if(response.error) {
				// there was an error. Fix it.
				$scope.submitting = false;
				$scope.errorMessage = response.error.message;
			} else {
				var token = response.id;

				CustomAction.chargeCard(subTotal, $scope.totalCost, token).then(function(response) {
					if(response.data.success) {
						$modalInstance.close();
					}else {
						$scope.errorMessage = response.data.message;
						$scope.submitting = false;
					}
				});
			}
		}

		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};
	}]);


	modals.factory('modalFactory', ['$modal', 'CustomAction', function($modal, CustomAction) {
		return {
			'createLineItem': function(description, value, info) {
				return {
					'description': description,
					'value': value,
					'info': info
				}
			},

			'showPaymentModal': function(lineItems, resultCallback) {
				var modalInstance = $modal.open({
					templateUrl: '/static/js/templates/depositFundsModal.html',
					controller: 'deposit-funds-modal-controller',
					resolve: {
						'lineItems': function() {
							return lineItems;
						}
					}
				});
				if(resultCallback != null) {
					modalInstance.result.then(resultCallback);
				}
			},
			'showCashOutModal': function() {
				var modalInstance = $modal.open({
					templateUrl: '/static/js/templates/cashOutModal.html',
					controller: 'cash-out-modal-controller'
				});

				modalInstance.result.then(function (details) {
					CustomAction.cashOut(details.email, details.amount);
				});
			}
		}
	}]);
}());
