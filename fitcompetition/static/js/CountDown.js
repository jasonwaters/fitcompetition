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

    var Countdown = function(element, options) {
        this.$element = $(element);
        this.options = $.extend({}, $.fn.countdown.defaults, options);
        var targetDateAttr = this.$element.attr('data-targetdate');

        if(targetDateAttr) {
            this.options.targetDate = moment(targetDateAttr).toDate();
        }

        this.timer = null;
        this.elements = {
            days:this.$element.find('.days-value'),
            hours:this.$element.find('.hours-value'),
            mins:this.$element.find('.minutes-value'),
            secs:this.$element.find('.seconds-value')
        };

        this.$element.on('change', $.proxy(this.handleChange,this));
        this.start();
    };

    Countdown.prototype.start = function () {
        if(this.timer === null) {
            this.timer = setInterval($.proxy(this.handleUpdate,this), this.options.updateFrequency);
        }
    };

    Countdown.prototype.stop = function() {
        clearInterval(this.timer);
        this.timer = null;
    };

    Countdown.prototype.handleUpdate = function() {
        var now = new Date();
        var diff = (this.options.targetDate.getTime() - now.getTime() + 5)/MILLIS_PER_SECOND; //in seconds

        if (diff < 0) {
            this.stop();
        } else {
            var days = Math.floor(diff / SECONDS_PER_DAY);
            diff = diff % SECONDS_PER_DAY; //remaining seconds in excess of full days

            var hours = Math.floor(diff / SECONDS_PER_HOUR);
            diff = diff % SECONDS_PER_HOUR; //remaining seconds in excess of full hours

            var mins = Math.floor(diff / SECONDS_PER_MINUTE);
            diff = diff % SECONDS_PER_MINUTE; //remaining seconds in excess of full minutes

            var secs = Math.floor(diff);

            var stats = {
                'days': days,
                'hours': hours,
                'mins': mins,
                'secs': secs
            };

            this.$element.trigger($.Event('change', stats));
        }
    };

    Countdown.prototype.handleChange = function(evt) {
        this.elements.days.each(function() {
           var $this = $(this);
            $this.text(pad(evt.days,2));
        });
        this.elements.hours.each(function() {
           var $this = $(this);
            $this.text(pad(evt.hours,2));
        });
        this.elements.mins.each(function() {
           var $this = $(this);
            $this.text(pad(evt.mins,2));
        });
        this.elements.secs.each(function() {
           var $this = $(this);
            $this.text(pad(evt.secs,2));
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
        updateFrequency: 1000 //every second
    };

    $.fn.countdown.Constructor = Countdown;

    //Apply countdown automatically to any element with data-countdown
    $(document).ready(function () {
        return $('[data-waters=countdown]').countdown();
    });
})(jQuery);