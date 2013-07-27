(function ($) {
    "use strict";

    var MILLIS_PER_SECOND = 1000;
    var MINUTES_PER_HOUR = 60;
    var HOURS_PER_DAY = 24;

    var SECONDS_PER_MINUTE = 60;
    var SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR;
    var SECONDS_PER_DAY = SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY;

    function pad(num, size) {
        var s = num+"";
        while (s.length < size) s = "0" + s;
        return s;
    }

    function getTimeLeft(targetDate) {
        var days = 0, hours = 0, minutes = 0, secs = 0;

        var diff = (targetDate.getTime() - new Date().getTime() + 5)/MILLIS_PER_SECOND; //in seconds

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

    var Countdown = function(element, options) {
        this.$element = $(element);
        this.options = $.extend({}, $.fn.countdown.defaults, options);
        var targetDateAttr = this.$element.attr('data-targetdate');
        var paddingAttr = this.$element.attr('data-numberpadding');

        if(targetDateAttr) {
            this.options.targetDate = moment(targetDateAttr).toDate();
        }

        if(paddingAttr) {
            this.options.padding = parseInt(paddingAttr);
        }

        this.timer = null;
        this.elements = {
            days:this.$element.find('.days-value'),
            hours:this.$element.find('.hours-value'),
            mins:this.$element.find('.minutes-value'),
            secs:this.$element.find('.seconds-value')
        };

        this.$element.on('change', $.proxy(this.handleChange, this));
        this.start();
    };

    Countdown.prototype.start = function () {
        this.handleUpdate();
        if(this.timer === null) {
            this.timer = setInterval($.proxy(this.handleUpdate,this), this.options.updateFrequency);
        }
    };

    Countdown.prototype.stop = function() {
        clearInterval(this.timer);
        this.timer = null;
    };

    Countdown.prototype.handleUpdate = function() {
        var timeLeft = getTimeLeft(this.options.targetDate);

        if (timeLeft.diff > 0) {
            this.$element.trigger($.Event('change', timeLeft));
        }else {
            this.stop();
        }
    };

    Countdown.prototype.handleChange = function(evt) {
        var padding = this.options.padding;

        this.elements.days.each(function() {
            var $this = $(this);
            $this.text(pad(evt.days,padding));
        });
        this.elements.hours.each(function() {
            var $this = $(this);
            $this.text(pad(evt.hours,padding));
        });
        this.elements.mins.each(function() {
            var $this = $(this);
            $this.text(pad(evt.minutes,padding));
        });
        this.elements.secs.each(function() {
            var $this = $(this);
            $this.text(pad(evt.seconds,padding));
        });
    };

    $.fn.countdown = function (option) {
        return this.each(function() {
            var $this = $(this);
            var instance = $this.data('countdown');
            var options = typeof option === 'object' && option;

            if(!instance) {
                $this.data('countdown', (instance = new Countdown(this, options)));
            }

            if( typeof option === 'string') {
                instance[option]();
            }
        });
    };

    $.fn.countdown.defaults = {
        targetDate: moment().days(30).toDate(), //30 days from now
        padding: 2,
        updateFrequency: 1000 //every second
    };

    $.fn.countdown.Constructor = Countdown;

    //Apply countdown automatically to any element with data-countdown
    $(document).ready(function () {
        return $('[data-waters=countdown]').countdown();
    });
})(jQuery);