document.addEventListener('formset:added', function (event) {
    var $field = django.jQuery(event.target).find('textarea.recurrence-widget:not([id*="__prefix__"])');
    if ($field.length) {
        initRecurrenceWidget($field);
    }
});
