(function() {
    "use strict";

    $.cookie.defaults = {
        path: '/',
        expires: 365
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url === origin || url.slice(0, origin.length + 1) === origin + '/') ||
            (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        }
    });

	jQuery.validator.setDefaults({
		errorPlacement: function (error, element) {
			// if the input has a prepend or append element, put the validation msg after the parent div
			if (element.parent().hasClass('input-prepend') || element.parent().hasClass('input-append')) {
				error.insertAfter(element.parent());
				// else just place the validation message immediatly after the input
			} else {
				error.insertAfter(element);
			}
		},
		errorElement: "small", // contain the error msg in a small tag
		wrapper: "div", // wrap the error message and small tag in a div
		highlight: function (element) {
			$(element).closest('.form-group').addClass('has-error'); // add the Bootstrap error class to the control group
		},
		success: function (element) {
			$(element).closest('.form-group').removeClass('has-error'); // remove the Boostrap error class from the control group
		}
	});
})();