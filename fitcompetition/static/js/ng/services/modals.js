(function() {
	"use strict";

	function summarize(items) {
		return _.reduce(items, function(result, item) {
			return result + item['value'];
		},0);
	}

	var modals = angular.module('modals', ['api', 'ui.bootstrap', 'angularPayments', 'slugifier']);

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

	modals.controller('deposit-funds-modal-controller', ['$scope','$modalInstance','modalFactory','lineItems', 'CustomAction', 'Common', function ($scope, $modalInstance, modalFactory, lineItems, CustomAction, Common) {
		var subTotal = summarize(lineItems);

		$scope.details = {
			'remember': true,
			'submitting': false,
			'errorMessage': null,
			'existingCard': null,
			'isCustomer': FC.account.isStripeCustomer
		};

		$scope.newcard = {
			'name': null,
			'number': null,
			'expiry': null,
			'cvc': null
		};

		if(FC.account.isStripeCustomer) {
			CustomAction.getStripeCustomer().then(function(response) {
				if(response.data.success) {
					$scope.details.existingCard = response.data.card;
				}
			});
		}

		var transactionFee = ((subTotal +.30)/(1-0.029)) - subTotal;
		transactionFee = Math.round(transactionFee*100)/100; //round to two decimal places

		lineItems.push(modalFactory.createLineItem("Transaction Fee", transactionFee, "Transaction fees apply only when you put money in the pot."));
		$scope.details.lineItems = lineItems;

		$scope.details.totalCost = summarize($scope.details.lineItems);

		function handleStripe(status, response){
			if(response.error) {
				// there was an error. Fix it.
				$scope.details.submitting = false;
				$scope.details.errorMessage = response.error.message;
			} else {
				var token = response.id;

				CustomAction.chargeCard(subTotal, $scope.details.totalCost, token, $scope.details.remember).then(function(response) {
					if(response.data.success) {
						$modalInstance.close();
					}else {
						$scope.details.errorMessage = response.data.message;
						$scope.details.submitting = false;
					}
				});
			}
		}

		$scope.replaceCardDetails = function() {
			CustomAction.deleteCard();
			$scope.details.existingCard = null;
		};

		$scope.ok = function() {
			$scope.details.errorMessage = null;
			$scope.details.submitting = true;

			if($scope.details.existingCard != null) {
				CustomAction.chargeCard(subTotal, $scope.details.totalCost, null, true).then(function(response) {
					if(response.data.success) {
						$modalInstance.close();
					}else {
						$scope.details.errorMessage = response.data.message;
						$scope.details.submitting = false;
					}
				});
			}else {
				var exp = Common.parseExpiry($scope.newcard.expiry);
				Stripe.card.createToken({
					'name': $scope.newcard.name,
					'number': $scope.newcard.number.replace(/ /g, ''),
					'exp_month': exp.month,
					'exp_year': exp.year,
					'cvc': $scope.newcard.cvc
				}, function () {
					var args = arguments;
					$scope.$apply(function () {
						handleStripe.apply($scope, args);
					});
				});
			}
		};

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
