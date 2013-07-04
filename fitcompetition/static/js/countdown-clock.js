(function () {
    var MILLIS_PER_SECOND = 1000;
    var MINUTES_PER_HOUR = 60;
    var HOURS_PER_DAY = 24;

    var SECONDS_PER_MINUTE = 60;
    var SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR;
    var SECONDS_PER_DAY = SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY;

    function getTimeLeft(targetDate) {
        var days = 0, hours = 0, minutes = 0, secs = 0;

        var now = new Date();
        var diff = (targetDate.getTime() - now.getTime() + 5)/MILLIS_PER_SECOND; //in seconds

        if (diff >= 0) {
            days = Math.floor(diff / SECONDS_PER_DAY);
            diff = diff % SECONDS_PER_DAY; //remaining seconds in excess of full days

            hours = Math.floor(diff / SECONDS_PER_HOUR);
            diff = diff % SECONDS_PER_HOUR; //remaining seconds in excess of full hours

            minutes = Math.floor(diff / SECONDS_PER_MINUTE);
            diff = diff % SECONDS_PER_MINUTE; //remaining seconds in excess of full minutes

            secs = Math.floor(diff);
        }

        return {
            'diff': diff,
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': secs
        };
    }

    var countdownApp = angular.module('countdown', []);

    countdownApp.value('targetDate', moment(COUNTDOWN_TARGET_DATE).toDate());

    countdownApp.filter('pad', function() {
        return function (value, size) {
            var s = value+"";
            while (s.length < size) s = "0" + s;
            return s;
        };
    });

    countdownApp.controller('CountdownController', function($scope, targetDate) {
        var timer = setInterval(function() {
            var timeLeft = getTimeLeft(targetDate);

            if (timeLeft.diff < 0) {
                clearInterval(timer);
                timer = null;
            }

            $scope.$apply(function() {
               $scope.data = timeLeft;
            });
        }, 1000);

        $scope.data = getTimeLeft(targetDate);
    });
})();